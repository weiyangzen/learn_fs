# sources/storage-engines/tikv/components/tikv_util/src/worker/metrics.rs

Purpose: Prometheus metric definitions for classic workers.

Important APIs/types/functions: `WORKER_PENDING_TASK_VEC` and `WORKER_HANDLED_TASK_VEC`.

Control flow: lazy-static registration creates an `IntGaugeVec` labeled by worker name for pending plus running work and an `IntCounterVec` for completed tasks.

State and persistence: metric state is process-local and exported through Prometheus; no durable persistence.

Dependencies/integration: used by `worker/future.rs` and `worker/pool.rs` schedulers and runners.

Risks: metric labels depend on stable worker names; duplicated labels intentionally aggregate clones of the same scheduler.

Test signals: worker tests assert handled counts in timer-backed lazy workers; metric registration itself is not independently tested.
