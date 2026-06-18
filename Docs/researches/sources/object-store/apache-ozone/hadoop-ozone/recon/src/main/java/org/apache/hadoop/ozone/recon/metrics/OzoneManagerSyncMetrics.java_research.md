## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/OzoneManagerSyncMetrics.java

Purpose: Metrics2 source for Recon synchronization with Ozone Manager metadata.

Important APIs/types/functions: static `create`; `unRegister`; increment methods for snapshot/delta request failures and totals; `incrNumUpdatesInDeltaTotal`; sequence-number lag setter/getter; test getters.

Control flow: delta update increments both total updates and non-zero delta request count, then recomputes average updates per non-zero request. Snapshot and failure counters are straightforward increments.

State and persistence: in-memory metrics; no durable writes. Integrates with OM sync tasks and Hadoop Metrics2.

Risks: average only accounts for non-zero delta requests by design; zero-update requests are not counted in denominator. Metrics fields are injected by Metrics2 annotations after registration. Tests should cover average calculation, sequence lag, failure counters, unregister, and zero-update semantics.
