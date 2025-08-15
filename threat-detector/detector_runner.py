import json
import logging
import sys
from kafka import KafkaConsumer, KafkaProducer

from detection_model import DetectionModel
from alert_model import Alert 

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    stream=sys.stdout
)

# setup 
detection_model = DetectionModel(model_path='xgb_sharedcols_v1.pkl', name='threat_detector')  

consumer = KafkaConsumer(
    'normalized-logs',
    bootstrap_servers='message-broker:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    group_id='threat-detector-group',
    enable_auto_commit=False
)

producer = KafkaProducer(
    bootstrap_servers='message-broker:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


# Process messages
logging.info("Starting message processing loop")
for msg in consumer:
    try:
        logging.info(f"Received message: {msg.value}")
        sample = msg.value    

        detection_result = detection_model.detect(sample)
        logging.info(f'Results: {detection_result}')

        if detection_result and detection_result.get("label") != 0:
            logging.info(f"Detected threat with confidence {detection_result['confidence']}")
            alert = Alert(
                confidence=detection_result["confidence"],
                log_data=sample
            )
            producer.send('threat-detection-alerts', alert.to_dict())
            producer.flush()
            print(f"Sent alert to 'threat-detection-alerts' topic!")

        consumer.commit()

    except Exception as e:
        logging.error(f"Error during detection: {e}")

