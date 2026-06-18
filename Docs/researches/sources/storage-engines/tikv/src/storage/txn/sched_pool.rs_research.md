# sources/storage-engines/tikv/src/storage/txn/sched_pool.rs

## Purpose
`sched_pool.rs` builds and manages the transaction scheduler worker pools. It hides whether tasks run on traditional high/normal priority pools or a resource-control-aware priority pool, initializes scheduler-thread TLS state, and batches per-thread metrics before flushing them to Prometheus and PD flow-stat reporters.

## Important APIs, types, and functions
`SchedLocalMetrics` stores thread-local scan statistics keyed by command name, a local key-read histogram vector, and local `WriteStats`. `TLS_SCHED_METRICS` owns those accumulators per scheduler worker thread. `TLS_FEATURE_GATE` stores the feature-gate snapshot that command execution checks through `tls_can_enable`.

`SchedTicker<R>` implements `PoolTicker::on_tick` and calls `tls_flush`, making metric flushes part of Yatp pool ticking. `QueueType` selects `Vanilla` or `Dynamic` queue behavior. `VanillaQueue` wraps separate `FuturePool`s for high-priority and normal/low-priority commands. `PriorityQueue` wraps a priority future pool plus `ResourceController` and `ResourceGroupManager`; it converts command priority into Yatp multilevel extras and wraps futures in `ControlledFuture` plus a resource limiter.

`SchedPool::new` builds all pools with `YatpPoolBuilder`, setting thread counts, names, task wait/exec metrics, TLS engine initialization, foreground-write IO type, TLS feature-gate initialization, TLS engine teardown, and final metric flush on worker stop. `SchedPool::spawn` dispatches according to `QueueType` and whether resource control is currently customized. `scale_pool_size` and `get_pool_size` expose dynamic sizing. TLS helpers collect scan details, key-read histograms, PD query counts, and feature-gate checks.

## Control flow
Scheduler code submits every command future through `SchedPool::spawn`, passing request source, resource metadata, command priority, and write-byte estimate. In vanilla mode high-priority commands use the high-priority pool, all others use the regular pool. In dynamic mode, if resource control is customized, tasks enter the priority pool with metadata and resource limiter; otherwise they fall back to vanilla routing.

When a scheduler worker starts, it installs a cloned engine into TLS, sets IO type to foreground write, and copies the feature gate to TLS. Command execution accumulates statistics through TLS helper functions. On pool ticks and worker shutdown, `tls_flush` drains those local values into global metrics and reports write stats to PD.

## State and persistence behavior
This file does not directly persist user data. It manages execution state for scheduler worker pools and per-thread metrics. The TLS engine pointer is critical process state: command execution later uses `with_tls_engine` and relies on the pool's `after_start`/`before_stop` invariants. Local write stats become PD flow-stat reports, which affect load reporting and scheduling outside this file.

## Dependencies and integration points
The pool integrates `tikv_util::yatp_pool`, `yatp::queue::Extras`, resource-control futures and managers, PD feature gates, raftstore write stats, file-system IO tagging, storage engines, and storage metrics. Thread-name constants make these pools visible in diagnostics. It is consumed by `TxnScheduler` for normal command execution, delayed admission-control tasks, lock-wait wakeups, and async background work.

## Risks and edge cases
`PriorityQueue::spawn` unwraps UTF-8 conversion of the resource group name with a default fallback, so invalid metadata silently maps to the default group. `SchedPool::new` unwraps `resource_mgr` when `resource_ctl` is present; callers must pass both together. Dynamic mode can switch back to vanilla when the resource controller is not customized, so behavior depends on runtime resource-control state rather than only construction-time configuration. TLS engine setup and teardown rely on generic type consistency; the comments explicitly mark the safety invariant.

Metric flushing is opportunistic through pool ticks and stop hooks. If a thread is busy for a long time, local metric visibility can lag. `PriorityQueue` currently uses random task IDs, so task identity is not stable across retries or logs.

## Test signals
No tests live in this file. Indirect coverage comes from scheduler tests that run commands through the pool and from resource-control integration tests elsewhere. Valuable direct tests would cover queue selection in vanilla versus dynamic mode, fallback when resource control is not customized, pool scaling for high-priority and normal pools, TLS feature-gate replacement, and that `tls_flush` drains scan details and write stats exactly once.
