# sources/storage-engines/tikv/components/raftstore/src/store/worker/disk_check.rs

## Purpose
This worker measures disk I/O latency for TiKV health inspection. It writes a small probe file, records the observed latency into a `LatencyInspector`, and finishes the inspector callback asynchronously through a bound background worker.

## Important APIs, Types, and Functions
- `Task::InspectLatency { inspector }` carries a health-controller latency inspector.
- `Runner::new(inspect_dir)` targets `.disk_latency_inspector.tmp` inside the inspect directory.
- `Runner::dummy` creates a local test runner.
- `bind_background_worker` attaches a `tikv_util::worker::Worker` for async execution.
- `inspect` delegates to `ProbeRunner::probe_once`.
- `execute` drains at most one queued task with `try_recv`.

## Control Flow
`run` tries to enqueue the incoming task into a bounded channel of capacity three. If enqueue succeeds and a background worker is bound, it clones the runner and spawns an async task that calls `execute`. `execute` receives one pending inspect task, runs a disk probe, records the duration with `inspector.record_apply_process`, and calls `inspector.finish`. Probe failures and enqueue failures are logged.

## State and Persistence Behavior
The worker creates/overwrites a temporary probe file via `ProbeRunner` and removes it in `Drop`. The bounded channel intentionally drops pressure when too many inspections arrive; older or excess health probes are treated as stale. It records latency into the supplied inspector but does not persist health state itself.

## Dependencies and Integration Points
It depends on crossbeam bounded channels, `health_controller::types::LatencyInspector`, `tikv_util::worker::Worker`, and `crate::store::disk_probe::ProbeRunner`. It integrates with server health monitoring that schedules disk checks and consumes inspector completion callbacks.

## Risks and Edge Cases
If no background worker is bound, accepted tasks remain queued but are not executed until future runs with a worker, and capacity can fill. `execute` processes only one queued task per spawned async task. Drop always attempts to remove the probe path and logs if the file is already gone or cannot be removed.

## Test Signals
`test_disk_check_runner` binds a background worker, verifies a positive latency is recorded, then removes the worker and submits more inspections to verify they do not complete and capacity/backpressure prevents uncontrolled accumulation.
