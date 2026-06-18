# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/ContainerStat.java

Purpose: mutable aggregate of container statistics: max size, used bytes, key count, read/write bytes, and read/write counts.

Important APIs: default and full constructors, getters for seven `LongMetric` fields, `add`, `subtract`, and `toJsonString`.

Control flow and state: validates non-negative constructor inputs, stores each metric as a mutable `LongMetric`, and mutates in place on add/subtract. JSON serialization uses `JsonUtils` and returns null on `IOException`.

Dependencies and integration: used by `SCMMetrics` for last and cumulative container report statistics.

Risks: constructor checks `readBytes >= 0` twice and does not check `writeBytes >= 0`, allowing negative write bytes. `subtract` can produce negative values despite constructor guards. Test signals should cover JSON names, add/subtract math, negative validation including write bytes, and null handling.
