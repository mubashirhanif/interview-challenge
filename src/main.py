from PIL import Image
import pytesseract
import boto3
import os
import json
from io import BytesIO
import base64


def _ocr_tersseract(im_bytes):
    im = Image.open(BytesIO(im_bytes))
    ocr_result = pytesseract.image_to_data(im, output_type=pytesseract.Output.DATAFRAME)
    text = ocr_result[ocr_result.conf != -1]
    lines = ocr_result.groupby("line_num")["text"].fillna("").tolist()
    conf = text.groupby(["block_num"])["conf"].mean()
    combined_text = " ".join(lines)
    return combined_text, conf.at[1]


def _ocr_tersseract(im_bytes):
    im = Image.open(BytesIO(im_bytes))
    ocr_result = pytesseract.image_to_data(im, output_type=pytesseract.Output.DATAFRAME)
    text = ocr_result[ocr_result.conf != -1]
    lines = ocr_result.groupby("line_num")["text"].fillna("").tolist()
    conf = text.groupby(["block_num"])["conf"].mean()
    combined_text = " ".join(lines)
    return combined_text, conf.at[1]


def _ocr_aws(im_bytes):
    client = boto3.client("textract")
    response = client.detect_document_text(Document={"Bytes": im_bytes})
    lines = []
    confidances = []
    for block in response["Blocks"]:
        if block["BlockType"] == "LINE":
            lines.append(block["Text"])
            confidances.append(block["Confidence"])
    try:
        return " ".join(lines), sum(confidances) / len(confidances)
    except ZeroDivisionError:
        return "", 0


def ocr_internal_function(event, context):
    body = json.loads(event)
    im_bytes = base64.b64decode(body["image"])
    tess_text, tess_conf = _ocr_tersseract(im_bytes)
    aws_text, aws_conf = _ocr_aws(im_bytes)
    if aws_conf >= tess_conf:
        return json.dumps({"text": aws_text})
    return json.dumps({"text": tess_text})


def ocr_api_function(event, context):
    # Create the Lambda client
    lambda_client = boto3.client("lambda")
    func_name = os.environ.get("OCR_INTERNAL_FUNCTION_ARN", "")

    if not (event or event["body"] or event["body"]["image"]):
        return {"statusCode": 400, "body": "Image not found"}
    response = lambda_client.invoke(
        FunctionName=func_name,
        Payload=json.dumps(event["body"]),
    )
    return {"statusCode": 200, "body": response["Payload"].read()}
