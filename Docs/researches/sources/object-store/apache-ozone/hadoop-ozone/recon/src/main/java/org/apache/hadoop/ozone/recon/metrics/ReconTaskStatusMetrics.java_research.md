## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ReconTaskStatusMetrics.java

Purpose: Metrics2 source that exposes rows from the persistent `ReconTaskStatus` SQL table as metrics.

Important APIs/types/functions: injected `ReconTaskStatusDao`; `register`; `unregister`; `getMetrics`.

Control flow: each metrics collection calls `findAll()`, emits one record per task with a `type` tag, `lastUpdatedTimestamp` gauge, and `lastUpdatedSeqNumber` counter.

State and persistence: reads persistent SQL task status; no writes. Integrates with jOOQ generated DAO, Guice injection, and Metrics2.

Risks: metrics collection can hit the database on scrape path; DAO failures are not caught here. Using a counter for sequence number represents a point-in-time value, not a monotonically incremented metric source. Tests should cover empty table, multiple rows, tag values, register/unregister, and DAO exception behavior.
