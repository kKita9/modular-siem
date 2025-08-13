import json
import logging
from kafka import KafkaConsumer, KafkaProducer

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
    if entry.get("event_type") != "flow":
        logging.info(f"Skipping non-flow event: {entry.get('event_type')}")
        return None
    return flatten_entry(entry)

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
    logging.info(f"Received message: {msg.value}")
    parsed = parse_suricata_log(msg.value)
    if parsed:
        logging.info(f"Parsed message: {parsed}")
        producer.send('normalized-logs', parsed)
        logging.info("Sent parsed message to 'normalized-logs' topic")