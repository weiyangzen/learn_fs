# sources/object-store/daos/src/engine/sched.c

## Purpose
`sched.c` implements the DAOS engine's custom Argobots scheduler and request admission/throttling layer. It multiplexes network polling, NVMe polling, and generic ULT execution; queues pool-scoped requests; applies VOS space-pressure throttling; rejects overload early; tracks sleep/wakeup state; and monitors long-running or inactive ULTs.

## Important APIs, Types, and Functions
Key internal types are `sched_request`, `sched_pool_info`, `sched_req_info`, `stats_window`, `sched_cycle`, and `sched_data`. Exported functions include `dss_sched_init`, `dss_sched_fini`, `sched_req_enqueue`, `sched_req_get`, `sched_req_put`, `sched_req_sleep`, `sched_req_yield`, `sched_req_wakeup`, `sched_req_abort`, `sched_req_wait`, `sched_req_space_check`, `sched_stop`, `sched_cur_msec`, `sched_cur_seq`, `sched_create_ult`, `sched_cond_wait`, `sched_cond_wait_for_business`, and `sched_exec_time`.

## Control Flow
Incoming RPCs enter through `sched_req_enqueue`. Anonymous or disabled-priority requests are immediately turned into ULTs; pool-scoped requests are wrapped in `sched_request`, placed in FIFO or sorted retry heap for update/fetch, or per-type lists for GC/scrub/migrate. Each scheduler cycle starts with network poll, refreshes timestamps, wakes sleeping requests, processes pool queues, calculates per-type kick limits, then runs generic ULTs and periodically NVMe poll ULTs. `check_space_pressure` queries VOS pool space, maps free-space ratios to pressure levels, and drives `throttle_io` or `throttle_sys`.

## State and Persistence Behavior
Scheduler state lives per xstream in `struct sched_info`, including idle request cache, sleep queue, FIFO queue, retry heap, pool hash, counters, telemetry nodes, current sequence/time, and watchdog fields. Pool state is cached in `sched_pool_info` records keyed by pool UUID and purged when VOS reports pool deletion and no requests/GC ULTs remain. No state is persisted, but scheduling decisions can affect externally visible latency, timeout, and ENOSPACE behavior.

## Dependencies and Integration Points
The scheduler integrates tightly with Argobots schedulers/pools/threads/tasks/futures, DAOS telemetry, VOS space queries, BIO NVMe polling, server xstream metadata, DAOS fail/error conventions, and module-provided request attributes. `srv.c` creates the scheduler for each xstream and the RPC handler feeds module request attributes into it.

## Risks
This is high-risk concurrency code. Queue counters, heap membership, request ownership, and GC sleeping counts must stay balanced across yield/sleep/wakeup/abort/shutdown. The pool hash is no-lock because scheduling runs on one xstream, so cross-xstream access would be unsafe. Overload estimation is approximate and may reject too aggressively or too late. Scheduler monitor intentionally kills the engine on prolonged inactivity when configured. Time moving backward is handled with warnings but may affect sleeps and watchdogs.

## Test Signals
Important signals include queue counter assertions, telemetry for wait/sleep/reject/cycle duration, overload retry behavior under large queues, VOS space-pressure throttling, retried RPC heap ordering, sleep wakeup timing, shutdown draining with sleeping requests, scheduler watchdog warnings, monitor SIGKILL behavior under injected stalls, and Argobots pool lifecycle tests.
