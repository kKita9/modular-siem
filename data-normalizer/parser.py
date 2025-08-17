import json
import logging
from kafka import KafkaConsumer, KafkaProducer
from normalized_log import NormalizedLog

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def flatten_entry(entry):
    flat = {}
    for k, v in entry.items():
        if isinstance(v, dict):
            for sub_k, sub_v in v.items():
                flat[f"{k}.{sub_k}"] = sub_v
        else:
            flat[k] = v
    return flat

def parse_suricata_log(entry):
    try:
        parsed = json.loads(entry)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON from 'message': {e}")
        return None

    return flatten_entry(parsed)


# Parser mapping
PARSERS = {
    'suricata': parse_suricata_log,
    # 'other_log_type': parse_other_log_type,
}

def get_parser(source_type):
    return PARSERS.get(source_type)

# Kafka setup
logging.info("Starting Kafka consumer and producer")
consumer = KafkaConsumer(
    'raw-logs',
    bootstrap_servers='message-broker:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    group_id='normalizer-group'
)

producer = KafkaProducer(
    bootstrap_servers='message-broker:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Process messages
logging.info("Starting message processing loop")
for msg in consumer:
    raw_message = msg.value
    source_type = raw_message.get('source_type')
    
    logging.info(f"Received message from source_type: {source_type}")

    if not source_type:
        logging.warning("Message without 'source_type' field. Skipping.")
        continue

    parser = get_parser(source_type)
    if not parser:
        logging.warning(f"No parser found for source_type: {source_type}. Skipping.")
        continue

    parsed = parser(raw_message.get('message'))
    if parsed:
        logging.info(f"Parsed message from {source_type}!")
        siem_metadata = {
            "source_type": raw_message.get("source_type"),
            "sensor_id": raw_message.get("sensor_id"),
            "env": raw_message.get("env"),
            "region": raw_message.get("region"),
            "host": raw_message.get("host", {}).get("name")
        }
        normalized_log = NormalizedLog(siem_metadata, parsed)
        producer.send('normalized-logs', normalized_log.to_dict())
        producer.flush()
        logging.info("Sent parsed message to 'normalized-logs' topic")