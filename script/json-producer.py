import argparse
import json
import signal
import sys
import time
from collections import defaultdict
from pprint import pprint
from random import choice, shuffle

from kafka import KafkaProducer

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
    return rv


def make_one(level):
    return json.dumps({
        "timestamp": int(time.monotonic_ns() / 1000),
        "level": level,
        "message": f"its a {level}!",
    })


def main():
    probs = make_propabilities(
        info=8,
        warn=4,
        error=2,
        crit=1,
    )

    shuffle(probs)

    args = parser.parse_args()
    delay = 1.0 / float(args.mps)
    counter = defaultdict(int)

    producer = KafkaProducer(bootstrap_servers=args.broker, acks=1)

    def sig_handler(signum, frame):
        producer.flush()
        pprint(dict(counter.items()), stream=sys.stderr)
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)

    while True:
        level = choice(probs)
        producer.send(args.topic, make_one(level).encode('utf8'))
        counter[level] += 1
        time.sleep(delay)


main()
