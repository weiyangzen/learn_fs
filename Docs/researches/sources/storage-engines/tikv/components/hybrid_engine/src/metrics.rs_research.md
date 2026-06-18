# sources/storage-engines/tikv/components/hybrid_engine/src/metrics.rs

Purpose: Prometheus metrics for hybrid snapshot choice, cache snapshot failure reasons, and transfer-leader warmup.

Important APIs/types/functions: static metric label enums `SnapshotType`, `FailedReason`, `TransferLeaderWarmupType`; lazy registered `IntCounterVec`s and auto-flush static wrappers.

Control flow: lazy registration on first access; observers increment counters when snapshots are used/wasted/fallback and when transfer-leader warmup is requested/performed/skipped.

State and persistence: process-local counters exported through Prometheus; reset on restart.

Dependencies/integration: used by snapshot and load-eviction observers; depends on `prometheus` and `prometheus-static-metric`.

Risks: public typo `STAIC` is baked into current imports; `no_read_ts` label is defined but unused in these files.

Test signals: no direct metric assertions.
