## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ReconSyncMetrics.java

Purpose: Metrics2 source for OM delta sync and full snapshot sync operations.

Important APIs/types/functions: static `create`; `unRegister`; update/increment methods for delta fetch duration/success/failures/data size, delta apply duration/failures, full DB request latency/fetch count, snapshot size/download success/failure; getters for tests.

Control flow: sync code calls counters/rates at relevant fetch, apply, and snapshot stages. Rates use `MutableRate`, counters use `MutableCounterLong`.

State and persistence: in-memory metrics only. Integrates with Recon OM sync code and Metrics2.

Risks: no success counter for delta apply, only failures and duration. Metrics fields rely on registration for initialization. Tests should validate all increments/rates, snapshot counters, and lifecycle unregister.
