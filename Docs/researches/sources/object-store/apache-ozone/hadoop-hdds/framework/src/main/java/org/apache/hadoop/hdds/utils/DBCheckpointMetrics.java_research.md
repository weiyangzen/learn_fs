# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/DBCheckpointMetrics.java

Purpose: `DBCheckpointMetrics` tracks timing and count statistics for database checkpoint creation and streaming.

Important APIs/types/functions: `create(parent)` registers the source with Metrics2. `unRegister()` unregisters it. Setters update gauges for last creation time, last streaming time, and number of excluded SST files. Increment methods update checkpoint, failure, and incremental-checkpoint counters. Visible-for-testing getters expose current values.

Control flow: `DBCheckpointServlet` updates creation time after checkpoint creation, streaming time after writing, excluded SST count, total checkpoint count, incremental count when exclusions are used, and failure count on exceptions.

State and persistence: in-process Metrics2 gauges/counters only; no durable history.

Dependencies/integration: depends on Hadoop Metrics2 annotations/mutable metrics. Used by OM/SCM checkpoint servlet paths and exposed through service metrics.

Risks: static `SOURCE_NAME` can conflict if multiple DB checkpoint metrics are registered in one metrics system without namespacing. Metrics fields require Metrics2 registration.

Test signals: OM/SCM DB checkpoint servlet tests assert metrics such as checkpoint count, creation time, and streaming time. Transfer tests assert incremental/failure metric behavior.
