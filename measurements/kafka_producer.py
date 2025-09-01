import os
import json
import logging
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import KafkaError, TopicAlreadyExistsError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ShellyKafkaProducer:
    def __init__(self):
        self.broker = os.getenv("KAFKA_BROKER", "localhost:9092")
        self.topic = os.getenv("KAFKA_TOPIC", "shelly_data")
        self.producer = None

        # Ensure topic exists
        self._create_topic_if_not_exists()

        # Connect producer
        self._connect()

    def _create_topic_if_not_exists(self):
        """Create Kafka topic if it does not exist"""
        try:
            admin = KafkaAdminClient(bootstrap_servers=[self.broker])

            topic = NewTopic(
                name=self.topic,
                num_partitions=int(os.getenv("KAFKA_TOPIC_PARTITIONS", "1")),
                replication_factor=int(os.getenv("KAFKA_TOPIC_REPLICATION", "1"))
            )

            admin.create_topics([topic])
            logger.info(f"[Kafka] Topic '{self.topic}' created")
        except TopicAlreadyExistsError:
            logger.info(f"[Kafka] Topic '{self.topic}' already exists")
        except Exception as e:
            logger.warning(f"[Kafka] Could not create topic '{self.topic}': {e}")
        finally:
            try:
                admin.close()
            except Exception:
                pass

    def _connect(self):
        """Initialize Kafka producer, log error if broker not found"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[self.broker],
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            logger.info(f"[Kafka] Connected to broker {self.broker}")
        except KafkaError as e:
            self.producer = None
            logger.error(f"[Kafka] Cannot connect to broker {self.broker}: {e}")

    def send(self, message: dict):
        """Send a message to Kafka topic, log error if not connected"""
        if not self.producer:
            logger.warning(f"[Kafka] Producer not available. Message not sent: {message}")
            return
        try:
            self.producer.send(self.topic, message)
            self.producer.flush()
            logger.info(f"[Kafka] Message sent to {self.topic}: {message}")
        except KafkaError as e:
            logger.error(f"[Kafka] Failed to send message: {e}")


# Singleton instance
kafka_producer = ShellyKafkaProducer()
