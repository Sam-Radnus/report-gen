"""
Polling service: poll messages from SQS or MKS (Kafka) based on configuration.
Set QUEUE_TYPE to 'sqs' or 'mks' and the corresponding env vars.
"""
import json
import os
from typing import Any, List

from dotenv import load_dotenv

load_dotenv()

# Configuration: QUEUE_TYPE = 'sqs' | 'mks'
QUEUE_TYPE = os.environ.get("QUEUE_TYPE", "sqs").lower()

# SQS config
SQS_QUEUE_URL = os.environ.get("SQS_QUEUE_URL", "")
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-2")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_KEY", "")
SQS_MAX_MESSAGES = int(os.environ.get("SQS_MAX_MESSAGES", "10"))
SQS_WAIT_TIME_SECONDS = int(os.environ.get("SQS_WAIT_TIME_SECONDS", "20"))

# MKS (Kafka) config
MKS_BOOTSTRAP_SERVERS = os.environ.get("MKS_BOOTSTRAP_SERVERS", "localhost:9092")
MKS_TOPIC = os.environ.get("MKS_TOPIC", "report-queue")
MKS_GROUP_ID = os.environ.get("MKS_GROUP_ID", "report-consumer")
MKS_POLL_TIMEOUT_MS = int(os.environ.get("MKS_POLL_TIMEOUT_MS", "5000"))

_mks_consumer = None


def _get_sqs_client():
    import boto3
    return boto3.client("sqs", region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


def _get_mks_consumer():
    global _mks_consumer
    if _mks_consumer is None:
        from kafka import KafkaConsumer
        servers = [s.strip() for s in MKS_BOOTSTRAP_SERVERS.split(",")]
        _mks_consumer = KafkaConsumer(
            MKS_TOPIC,
            bootstrap_servers=servers,
            group_id=MKS_GROUP_ID,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")) if m else None,
            auto_offset_reset="earliest",
        )
    return _mks_consumer


def poll_messages() -> List[dict]:
    """
    Poll messages from the configured queue (SQS or MKS).
    Returns a list of dicts, each with at least:
      - 'body': parsed or raw message payload
      - 'receipt_handle' (SQS) or 'record' (MKS) for ack/delete/commit.
    """
    if QUEUE_TYPE == "sqs":
        return _poll_sqs()
    if QUEUE_TYPE == "mks":
        return _poll_mks()
    raise ValueError(f"Unknown QUEUE_TYPE: {QUEUE_TYPE}. Use 'sqs' or 'mks'.")


def _poll_sqs() -> List[dict]:
    if not SQS_QUEUE_URL:
        raise ValueError("SQS_QUEUE_URL must be set when QUEUE_TYPE=sqs")
    client = _get_sqs_client()
    resp = client.receive_message(
        QueueUrl=SQS_QUEUE_URL,
        MaxNumberOfMessages=SQS_MAX_MESSAGES,
        WaitTimeSeconds=SQS_WAIT_TIME_SECONDS,
        MessageAttributeNames=["All"],
    )
    messages = resp.get("Messages") or []
    out = []
    for m in messages:
        body = m.get("Body", "")
        try:
            body = json.loads(body)
        except (TypeError, json.JSONDecodeError):
            pass
        out.append({
            "message_id": m.get("MessageId"),
            "body": body,
            "receipt_handle": m.get("ReceiptHandle"),
            "_raw": m,
        })
    return out


def _poll_mks() -> List[dict]:
    consumer = _get_mks_consumer()
    raw = consumer.poll(timeout_ms=MKS_POLL_TIMEOUT_MS)
    out = []
    for _topic_partition, records in raw.items():
        for record in records:
            body = record.value
            if body is None or (isinstance(body, bytes)):
                body = body.decode("utf-8") if isinstance(body, bytes) else (body or "")
            try:
                if isinstance(body, str) and body.strip().startswith("{"):
                    body = json.loads(body)
            except json.JSONDecodeError:
                pass
            out.append({
                "message_id": f"{record.topic}:{record.partition}:{record.offset}",
                "body": body,
                "record": record,
                "topic": record.topic,
                "partition": record.partition,
                "offset": record.offset,
            })
    return out


def delete_message(receipt: Any) -> None:
    """
    Delete/ack a message after processing.
    For SQS: pass the 'receipt_handle' from the polled message.
    For MKS: no-op per message (commit is handled by consumer group); receipt is ignored.
    """
    if QUEUE_TYPE == "sqs" and receipt:
        client = _get_sqs_client()
        client.delete_message(QueueUrl=SQS_QUEUE_URL, ReceiptHandle=receipt)
    # MKS: offset is committed by consumer group; optional manual commit can be added if needed

if __name__ == "__main__":
    messages = poll_messages()
    print(messages)