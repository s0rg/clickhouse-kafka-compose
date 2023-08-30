import argparse
import json
import random
import signal
import sys
import time
from collections import defaultdict

from kafka import KafkaAdminClient, KafkaProducer
from kafka.admin import NewTopic
from kafka.errors import NoBrokersAvailable, TopicAlreadyExistsError

parser = argparse.ArgumentParser(
    description="json producer for clickhouse-test-lab")
parser.add_argument("--mps",
                    type=int,
                    default=10,
                    help="average message-per-second rate (default: 10)")
parser.add_argument("--broker",
                    default="127.0.0.1:19092",
                    help="kafka uri (default: 127.0.0.1:19092)")
parser.add_argument("--topic",
                    default="event-queue",
                    help="topic (default: event-queue)")


def make_propabilities(**kw):
    rv = []
    for k, w in kw.items():
        rv.extend([k] * int(w))
    random.shuffle(rv)
    return rv


def make_one(level):
    return json.dumps({
        "timestamp": int(time.monotonic_ns() / 1000.0),
        "level": level,
        "message": f"its a {level}!",
    })


def create_topic(broker, topic, partitions=4, replica=1):
    adm = KafkaAdminClient(bootstrap_servers=broker)
    try:
        adm.create_topics([
            NewTopic(topic, partitions, replica),
        ])
    except TopicAlreadyExistsError:
        pass
    finally:
        adm.close()


def main():
    args = parser.parse_args()

    try:
        create_topic(args.broker, args.topic)
    except (NoBrokersAvailable, ValueError):
        print("[-] could not connect to broker: ", args.broker)
        sys.exit(1)

    counter = defaultdict(int)
    producer = KafkaProducer(
        bootstrap_servers=args.broker,
        client_id="json-producer",
        value_serializer=lambda s: s.encode('utf8'),
        acks=1,
    )

    def sig_handler(signum, frame):
        producer.close()
        print(dict(counter.items()), file=sys.stderr)
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)

    delay = 1.0 / float(args.mps)
    probs = make_propabilities(
        info=6,
        warn=3,
        error=2,
        crit=1,
    )

    while True:
        level = random.choice(probs)
        producer.send(args.topic, make_one(level))
        counter[level] += 1
        time.sleep(delay)


main()
