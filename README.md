[![License](https://img.shields.io/badge/license-MIT%20License-blue.svg)](https://github.com/s0rg/clickhouse-kafka-compose/blob/master/LICENSE)

# clickhouse-kafka-compose

Example docker-compose with clickhouse and kafka or redpanda as sources

# usage

Start original `kafka`-variant:

```shell
make kafka-up
```

Stop it:

```shell
make kafka-down
```

Stop and purge volumes:

```shell
make kafka-data-down
```

Same for `redpanda`-valiant

```shell
make redpanda-up
make redpanda-down
make redpanda-data-down
```

Send some data (stop it with `C-c`):

```shell
make produce
```

or with `kafkacat`

```shell
kcat -P -b 127.0.0.1:19092 -t event-queue < your-events.json
```

see: [init.sql](initdb.d/00-init.sql) for message structure details.

# exposed ports

Both variants:

- `127.0.0.1:19092` - kafka broker
- `127.0.0.1:9000` - clickhouse

Redpanda-only:

- `127.0.0.1:8080` - redpanda console (web ui)

# dependencies

Please, make sure you have installed [kafka-python](https://kafka-python.readthedocs.io/en/master/install.html) in order
to use provided `json-producer.py` script:

```shell
pip install kafka-python
```
