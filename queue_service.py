"""
Queue service: send messages to SQS or MKS (Kafka) based on configuration.
Set QUEUE_TYPE to 'sqs' or 'mks' and the corresponding env vars.
"""
import json
import os
from typing import Any
from dotenv import load_dotenv


load_dotenv()

# Configuration: QUEUE_TYPE = 'sqs' | 'mks'
QUEUE_TYPE = os.environ.get("QUEUE_TYPE", "sqs").lower()

# SQS config
SQS_QUEUE_URL = os.environ.get("SQS_QUEUE_URL", "")
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-2")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_KEY", "")
print(SQS_QUEUE_URL)
print()

# MKS (Kafka) config
MKS_BOOTSTRAP_SERVERS = os.environ.get("MKS_BOOTSTRAP_SERVERS", "localhost:9092")
MKS_TOPIC = os.environ.get("MKS_TOPIC", "report-queue")


def _get_sqs_client():
    import boto3
    return boto3.client("sqs", region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


def _get_mks_producer():
    from kafka import KafkaProducer
    servers = [s.strip() for s in MKS_BOOTSTRAP_SERVERS.split(",")]
    return KafkaProducer(
        bootstrap_servers=servers,
        value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8") if isinstance(v, dict) else str(v).encode("utf-8"),
    )


def send_message(message: Any) -> dict:
    """
    Send a message to the configured queue (SQS or MKS).
    message: dict or str; for SQS will be JSON-serialized as body.
    Returns result dict with 'MessageId' (SQS) or 'topic_partition_offset' (MKS).
    """
    if QUEUE_TYPE == "sqs":
        return _send_sqs(message)
    if QUEUE_TYPE == "mks":
        return _send_mks(message)
    raise ValueError(f"Unknown QUEUE_TYPE: {QUEUE_TYPE}. Use 'sqs' or 'mks'.")


def _send_sqs(message: Any) -> dict:
    if not SQS_QUEUE_URL:
        raise ValueError("SQS_QUEUE_URL must be set when QUEUE_TYPE=sqs")
    body = message if isinstance(message, str) else json.dumps(message, default=str)
    client = _get_sqs_client()
    resp = client.send_message(QueueUrl=SQS_QUEUE_URL, MessageBody=body)
    print(f"Message Sent {resp}")
    return {"MessageId": resp["MessageId"], "sqs_response": resp}


def _send_mks(message: Any) -> dict:
    producer = _get_mks_producer()
    value = message if isinstance(message, (dict, str)) else {"payload": str(message)}
    future = producer.send(MKS_TOPIC, value=value)
    record_metadata = future.get(timeout=10)
    producer.flush()
    return {
        "topic": record_metadata.topic,
        "partition": record_metadata.partition,
        "offset": record_metadata.offset,
    }