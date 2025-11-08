import json, os, boto3, urllib.parse

s3 = boto3.client("s3")
inspector = boto3.client("inspector2")

def _get_artifact(event, name):
    for a in event["CodePipeline.job"]["data"]["inputArtifacts"]:
        if a["name"] == name:
            loc = a["location"]["s3Location"]
            return loc["bucketName"], loc["objectKey"]
    raise Exception(f"Artifact {name} not found")

def _read_json_from_s3(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    return json.loads(obj["Body"].read())

def handler(event, context):
    b_img, k_img = _get_artifact(event, "ImageOutput")
    image_meta = _read_json_from_s3(b_img, k_img)
    repo = image_meta["imageUri"].split("/")[-1]
    digest = image_meta["digest"]

    b_sig, k_sig = _get_artifact(event, "VerifyOutput")
    sig = _read_json_from_s3(b_sig, k_sig)
    signature_ok = bool(sig.get("signatureVerified"))
    
    resp = inspector.list_findings(
        filterCriteria={
            "severity":[{"comparison":"EQUALS", "value":"CRITICAL"}],
            "ecrImageRepositoryName":[{"comparison":"EQUALS", "value": repo}],
            "ecrImageHash":[{"comparison":"EQUALS", "value": digest}],
        }
    )
    critical = len(resp.get("findings", []))

    if not signature_ok:
        msg = "FAIL: Signature missing or invalid."
        print(msg); raise Exception(msg)

    if critical > 0:
        msg = f"FAIL: {critical} CRITICAL vulnerabilities found for {repo}@{digest}."
        print(msg); raise Exception(msg)

    result = {"status":"PASS","repo":repo,"digest":digest}
    print(json.dumps(result))
    return result
