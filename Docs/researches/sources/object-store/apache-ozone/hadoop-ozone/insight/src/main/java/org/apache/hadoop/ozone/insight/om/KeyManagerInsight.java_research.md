<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/om/KeyManagerInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/om/KeyManagerInsight.java

Purpose: insight point for OM key-management behavior.

Important APIs: `getMetrics` creates OM metric groups for total keys and key operations plus per-operation success/failure counters for allocate, commit, lookup, list, and delete. `getRelatedLoggers` returns the `KeyManagerImpl` logger on OM. `getDescription` returns "OM Key Manager".

Control flow and integration: metrics are fetched from OM `/prom` and matched by hardcoded metric ids such as `om_metrics_num_key_allocate_fails`. Logs are streamed from OM with the KeyManager logger.

State and persistence: stateless descriptor builder. No persistence.

Risks and tests: metric names must match OM exporter names. Operation pluralization in descriptions is simple string concatenation and cosmetic only. No direct tests cover this insight point.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/om/KeyManagerInsight.java -->
