# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/PrometheusMetricsSinkUtil.java

## Purpose
`PrometheusMetricsSinkUtil` adapts Hadoop Metrics2 record/metric names and tags for Ozone's Prometheus sink. It normalizes names to Prometheus-friendly lowercase underscore form, handles special RocksDB metrics, and augments tags for RPC scheduler and UGI metrics.

## Important APIs and Types
`addTags` copies an input tag collection and conditionally adds username and servername tags. `prometheusName` combines record and metric names, with a RocksDB-specific path that keeps metric names already delimited by underscores. `getMetricName` and `getUsername` delegate split logic to `DecayRpcSchedulerUtil`.

## Control Flow and State
Name normalization uses a Guava `LoadingCache` capped at 100,000 entries. The normalizer splits camel-case and acronym boundaries, lowercases parts, and replaces non-alphanumeric runs with underscores. Cache load failures are logged and fall back to direct normalization.

## Persistence, Dependencies, and Integration
There is no persistence. Dependencies include Guava cache, Hadoop `MetricsTag`, Apache `StringUtils`, `RocksDBStoreMetrics.ROCKSDB_CONTEXT_PREFIX`, `DecayRpcSchedulerUtil`, and `UgiMetricsUtil`. It is part of HTTP metrics exposition.

## Risks and Test Signals
The cache can hold many unique metric names; its size cap should be validated under high-cardinality inputs. Name splitting can subtly change acronym-heavy names. Tests should cover RocksDB record names containing dots, camel-case/acronym normalization, illegal character replacement, tag preservation/order, username/servername tag injection, and cache fallback.
