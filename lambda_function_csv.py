import json
import csv
import os
import boto3
from datetime import datetime
from io import StringIO

from send_messages import batch_no

# Environment variables
SQS_QUEUE_URL = os.environ.get("SQS_QUEUE_URL")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-2")

sqs_client = boto3.client("sqs", region_name=AWS_REGION)
s3_client = boto3.client("s3", region_name=AWS_REGION)


def generate_invoice_csv(billing_data):
    """Generate properly formatted CSV invoice."""
    output = StringIO()
    writer = csv.writer(output)

    # --- Header ---
    writer.writerow(["INVOICE", "", "", ""])
    writer.writerow(["Invoice #", billing_data.get("invoice_number", "N/A"), "", ""])
    writer.writerow(["Date", billing_data.get("date", datetime.now().strftime("%Y-%m-%d")), "", ""])
    writer.writerow(["Due Date", billing_data.get("due_date", "N/A"), "", ""])
    writer.writerow([])

    # --- Customer ---
    writer.writerow(["Bill To", "", "", ""])
    customer = billing_data.get("customer", {})
    writer.writerow([customer.get("name", "N/A"), "", "", ""])

    for line in (customer.get("address", "") or "").split("\n"):
        writer.writerow([line, "", "", ""])

    writer.writerow([])

    # --- Items table ---
    writer.writerow(["Description", "Quantity", "Unit Price", "Amount"])

    items = billing_data.get("items", [])
    subtotal = 0

    for item in items:
        qty = item.get("quantity", 0)
        price = item.get("unit_price", 0)
        amount = qty * price
        subtotal += amount

        writer.writerow([
            item.get("description", ""),
            qty,
            f"{price:.2f}",
            f"{amount:.2f}",
        ])

    writer.writerow([])

    # --- Totals ---
    tax_rate = billing_data.get("tax_rate", 0)
    tax = subtotal * tax_rate
    total = subtotal + tax

    writer.writerow(["Subtotal", "", "", f"{subtotal:.2f}"])
    writer.writerow([f"Tax ({tax_rate * 100:.1f}%)", "", "", f"{tax:.2f}"])
    writer.writerow(["Total", "", "", f"{total:.2f}"])

    return output.getvalue()
    

def lambda_handler(event, context):
    processed_count = 0

    for record in event["Records"]:
        try:
            body = json.loads(record["body"])
            billing_id = body["id"]
            batch_no = body["batch_no"]
            billing_data = body["data"]

            print(f"batch-{batch_no} processing message {billing_id} with data \n {billing_data}")

            csv_content = generate_invoice_csv(billing_data)

            invoice_number = body.get(
                "invoice_number",
                f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )

            s3_key = f"invoices/batch-{batch_no}/{billing_id}/{invoice_number}.csv"

            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Body=csv_content.encode("utf-8"),
                ContentType="text/csv",
            )

            processed_count += 1

        except Exception as e:
            print(f"Error processing message: {str(e)}")

    return {"processed_messages": processed_count}