import os, json, random, boto3

rt = boto3.client("sagemaker-runtime")
ENDPOINT = os.environ["SAGEMAKER_ENDPOINT"]
VERSION = os.getenv("VERSION_TAG", "v1")
SAFE = os.getenv("SAFE_MODE", "false").lower() == "true"
THRESH = float(os.getenv("THRESHOLD", "0.7"))

def lambda_handler(event, _ctx):  # <-- renamed from handler
    body = _coerce_body(event)

    text = body.get("text")
    if text is None and "features" in body:
        text = f"{body['features']}"
    if text is None:
        text = "This is a placeholder text for inference."

    score = random.random()
    try:
        payload = json.dumps({"inputs": text})
        resp = rt.invoke_endpoint(
            EndpointName=ENDPOINT,
            ContentType="application/json",
            Accept="application/json",
            Body=payload,
        )
        txt = resp["Body"].read().decode("utf-8") if resp.get("Body") else "{}"
        parsed = _safe_json(txt)
        pos = _extract_positive_probability(parsed)
        if pos is not None:
            score = pos
    except Exception as e:
        print({"level":"error","msg":"SageMaker invoke failed","versionTag":VERSION,"error":str(e)})

    effective = min(1.0, THRESH + (0.05 if SAFE else 0.0))
    out = {
        "versionTag": VERSION,
        "safeMode": SAFE,
        "threshold": round(effective, 3),
        "score": round(float(score), 3),
        "flagged": float(score) >= effective,
        "echo": {"text": text[:120]}
    }
    print({"event":"inference", **out})
    return out

def _coerce_body(event):
    if isinstance(event, dict):
        if "body" in event and isinstance(event["body"], str):
            return _safe_json(event["body"])
        return event
    if isinstance(event, str):
        return _safe_json(event)
    return {}

def _safe_json(s):
    try: return json.loads(s or "{}")
    except Exception: return {}

def _softmax(logits):
    import math
    m = max(logits); exps = [math.exp(x - m) for x in logits]; d = sum(exps) or 1.0
    return [e/d for e in exps]

def _extract_positive_probability(parsed):
    if isinstance(parsed, dict) and "probabilities" in parsed:
        probs = parsed.get("probabilities")
        if isinstance(probs, list) and len(probs) >= 2:
            return float(probs[1])
    if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
        for item in parsed:
            label = str(item.get("label","")).upper()
            if "POSITIVE" in label and isinstance(item.get("score"), (int,float)):
                return float(item["score"])
        return float(max(parsed, key=lambda d: float(d.get("score",0))).get("score", 0.5))
    if isinstance(parsed, dict) and "logits" in parsed:
        logits = parsed.get("logits")
        if isinstance(logits, list) and len(logits) >= 2:
            return float(_softmax(logits)[1])
    return None
