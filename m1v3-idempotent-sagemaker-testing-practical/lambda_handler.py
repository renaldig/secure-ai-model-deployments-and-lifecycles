import os, json, time, random
import boto3

VERSION = os.getenv("VERSION_TAG", "m1v3")
SAFE = os.getenv("SAFE_MODE", "false").lower() == "true"
REDACT = os.getenv("REDACT_PII", "true").lower() == "true"
THRESH = float(os.getenv("THRESHOLD", "0.7"))
USE_MODEL = os.getenv("USE_MODEL", "false").lower() == "true"
TABLE = os.environ["EFFECTS_TABLE"]

ddb = boto3.client("dynamodb")

def model_score(features: dict) -> float:
    if not USE_MODEL:
        amt = float(features.get("amount", 0))
        return max(0.0, min(1.0, ((amt % 97) / 97.0) or random.random()))
    import boto3 as _b
    sm_region = os.getenv("SAGEMAKER_REGION") or os.getenv("AWS_REGION")
    rt = _b.client("sagemaker-runtime", region_name=sm_region)
    payload = json.dumps({"inputs": features.get("text") or str(features)})
    try:
        resp = rt.invoke_endpoint(
            EndpointName=os.environ["SAGEMAKER_ENDPOINT"],
            ContentType="application/json",
            Accept="application/json",
            Body=payload,
        )
        txt = resp["Body"].read().decode("utf-8") if resp.get("Body") else "{}"
        parsed = _safe_json(txt)
        if isinstance(parsed, dict) and "probabilities" in parsed:
            probs = parsed["probabilities"]
            return float(probs[1]) if isinstance(probs, list) and len(probs) > 1 else random.random()
        if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
            return float(max(d.get("score", 0) for d in parsed))
        return random.random()
    except Exception as e:
        print({"level":"error","msg":"invoke failed","versionTag":VERSION,"error":str(e)})
        return random.random()

def lambda_handler(event, _ctx):
    body = _coerce_body(event)
    ok, val_or_errs = _validate(body)
    if not ok:
        out = _resp(400, "Validation failed", errors=val_or_errs, echo=_safe_echo(body))
        print(_log("validation_failed", out))
        return out

    req = val_or_errs  # validated input
    eff_thresh = min(1.0, THRESH + (0.05 if SAFE else 0.0))
    score = max(0.0, min(1.0, model_score(req.get("features", {}))))
    flagged = score >= eff_thresh

    id_ = req["id"]
    idempo_status = None
    if req.get("compensate"):
        ddb.delete_item(TableName=TABLE, Key={"id": {"S": id_}})
        idempo_status = "COMPENSATED"
    else:
        try:
            ddb.put_item(
                TableName=TABLE,
                Item={
                    "id": {"S": id_},
                    "createdAt": {"N": str(int(time.time()))},
                    "flagged": {"BOOL": flagged},
                    "score": {"N": str(round(score, 6))},
                    "versionTag": {"S": VERSION},
                },
                ConditionExpression="attribute_not_exists(#id)",
                ExpressionAttributeNames={"#id": "id"},
            )
            idempo_status = "CREATED"
        except ddb.exceptions.ConditionalCheckFailedException:
            idempo_status = "REPLAYED"

    echo = _safe_echo(req) if REDACT else req
    out = _resp(200, "OK", versionTag=VERSION, safeMode=SAFE, threshold=round(eff_thresh,3),
                score=round(score,3), flagged=flagged, idempotency=idempo_status, echo=echo)
    print(_log("inference", out))
    return out

def _coerce_body(event):
    if isinstance(event, dict):
        if "body" in event and isinstance(event["body"], str):
            return _safe_json(event["body"])
        return event
    if isinstance(event, str):
        return _safe_json(event)
    return {}

def _validate(body):
    errs = []
    if not isinstance(body, dict):
        return False, ["Body must be a JSON object."]
    if not isinstance(body.get("id"), str) or not body["id"]:
        errs.append("id (string) is required.")
    feats = body.get("features", {})
    if feats and not isinstance(feats, dict):
        errs.append("features must be an object if provided.")
    if "amount" in feats and (not isinstance(feats["amount"], (int, float)) or feats["amount"] <= 0):
        errs.append("features.amount must be a number > 0 when present.")
    if "notes" in body and not isinstance(body["notes"], str):
        errs.append("notes must be a string if provided.")
    return (len(errs) == 0, body if len(errs) == 0 else errs)

def _safe_echo(obj):
    o = dict(obj)
    if "email" in o and isinstance(o["email"], str):
        local, _, domain = o["email"].partition("@")
        if domain:
            o["email"] = (local[:1] + "***" + local[-1:]) + "@" + domain
        else:
            o["email"] = "***"
    if "phone" in o and isinstance(o["phone"], str):
        o["phone"] = "".join("*" if c.isdigit() and i < len(o["phone"])-2 else c for i, c in enumerate(o["phone"]))
    if "notes" in o and isinstance(o["notes"], str):
        o["notes"] = o["notes"][:60]  # cap length
    return o

def _resp(statusCode, message, **kwargs):
    return {"statusCode": statusCode, "message": message, **kwargs}

def _safe_json(s):
    try: return json.loads(s or "{}")
    except Exception: return {}

def _log(event, payload):
    return json.dumps({"event": event, **payload})
