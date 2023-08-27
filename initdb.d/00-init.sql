-- stream

CREATE TABLE IF NOT EXISTS event_queue (
    timestamp UInt64,
    level     Enum('info' = 0, 'warn' = 1, 'error' = 2, 'crit' = 3),
    message   String
) ENGINE = Kafka(
    'kafka:9092',         -- broker
    'event-queue',        -- topic
    'click-event-reader', -- group
    'JSONEachRow'         -- format
);

-- table

CREATE TABLE IF NOT EXISTS daily_levels (
    day       Date,
    level     Enum('info' = 0, 'warn' = 1, 'error' = 2, 'crit' = 3),
    total     UInt64,
    partition UInt64,
    topic     String
) ENGINE = SummingMergeTree()
ORDER BY (day, level);

--- view

DROP VIEW IF EXISTS daily_levels_view;

CREATE MATERIALIZED VIEW daily_levels_view TO daily_levels AS
    SELECT
        toDate(toDateTime(timestamp)) AS day,
        level,
        count() as total
    FROM event_queue
    GROUP BY (day, level)
    ORDER BY (day, level);

-- query
-- select day, level, sum(total) from daily_levels group by (day, level);
