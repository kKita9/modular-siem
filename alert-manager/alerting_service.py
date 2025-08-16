from kafka import KafkaConsumer
import smtplib
import sys
import logging
from email.message import EmailMessage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    stream=sys.stdout
)

KAFKA_TOPIC = "threat-detection-alerts"
KAFKA_BOOTSTRAP_SERVERS = "message-broker:9092"
EMAIL_FROM = "siem@example.com"
EMAIL_TO = "999carol999@gmail.com"
SMTP_SERVER = "smtp-server"
SMTP_PORT = 1025

def send_email(subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.set_content(body)
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
        s.send_message(msg)

def main():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: m.decode("utf-8"),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="alerting"
    )
    logging.info("Listening for alerts...")
    for message in consumer:
        alert = message.value
        logging.info(f"Received alert: {alert}")
        send_email("SIEM Alert", alert)

if __name__ == "__main__":
    main()