import os, json, random

THRESHOLD   = float(os.getenv("THRESHOLD", "0.7"))
VERSION_TAG = os.getenv("VERSION_TAG", "v1")

def lambda_handler(event, context):
    text = (event or {}).get("text", "demo")
    score = round(random.random(), 3)
    flagged = score >= THRESHOLD
    return {
        "version_tag": VERSION_TAG,
        "threshold": THRESHOLD,
        "score": score,
        "flagged": flagged,
        "echo": {"text": text},
    }
