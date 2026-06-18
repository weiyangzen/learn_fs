## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ReconTaskControllerMetrics.java

Purpose: Metrics2 source for Recon task controller queue behavior and system-wide reprocess outcomes.

Important APIs/types/functions: static `create`; `unRegister`; setters/incrementers for queue size, buffered/dropped/processed events, checkpoint/execution/stage DB failures, successful reprocesses, and submitted reprocess events; test getters.

Control flow: task controller updates gauges/counters as queue events and reprocess phases occur. Metrics are annotation-backed.

State and persistence: in-memory metrics; no DB writes. Integrates with Recon task controller and Metrics2.

Risks: event count semantics must match producer code because this class does no validation. Tests should verify increments by arbitrary counts, queue gauge update, failure category counters, and unregister lifecycle.
