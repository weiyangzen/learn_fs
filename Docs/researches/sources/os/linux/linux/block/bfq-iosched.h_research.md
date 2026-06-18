# File Research: sources/os/linux/linux/block/bfq-iosched.h

`bfq-iosched.h` is the shared BFQ scheduler header. It defines constants, data structures, state flags, logging macros, and function prototypes used by BFQ’s main scheduler, WF2Q core, and cgroup layer.

Constants:
- BFQ supports three I/O priority classes and weights from `1` to `1000`.
- Ioprio-to-weight conversion uses coefficient `10`.
- Default queue ioprio is `4`; default group class is best-effort.
- Soft real-time queues can receive a large weight factor.
- `BFQ_MAX_ACTUATORS` is `8`, supporting per-actuator queueing and injection.

Scheduling structures:
- `bfq_service_tree`: per-ioprio-class active and idle rbtrees, first/last idle entity, virtual time, and weight sum.
- `bfq_sched_data`: a scheduler node containing three service trees, `in_service_entity`, `next_in_service`, and idle-class service timestamp.
- `bfq_entity`: generic schedulable node for either a queue or a group. It stores rb-node membership, B-WF2Q+ timestamps, service/budget, allocated requests, weight state, parent/sched_data links, priority-change state, and last child queue hints.
- `bfq_queue`: leaf request queue. It tracks references, ioprio, merge/cooperation state, request trees/fifo, budget and dispatch counters, flags, timing/thinktime stats, weight raising, waker relationships, burst membership, and actuator index.
- `bfq_io_cq`: per request-queue/io-context state, with async/sync queue matrices per actuator and persistent saved state for queue merge/split restoration.
- `bfq_data`: per-device scheduler state: dispatch list, root group, weight tree, busy queues, in-driver counts, hardware queueing samples, timers, in-service queue, dispatch/rate estimation, active/idle queues, tunables, low-latency and weight-raising state, OOM fallback queue, locks, bio merge context, async depths, and independent-access-range actuator data.

Cgroup/stat structures:
- `bfq_stat` and `bfqg_stats` store per-group accounting, with extra debug counters under `CONFIG_BFQ_CGROUP_DEBUG`.
- With group scheduling, `bfq_group_data` stores per-blkcg weight and `bfq_group` stores per-device group scheduler state, async queues, active/pending counters, rq-position tree, and stats.
- Without group scheduling, `bfq_group` is a minimal root-like container.

State and interfaces:
- `enum bfqq_state_flags` defines queue flags such as busy, wait_request, fifo_expire, short think time, sync, IO_bound, large burst, cooperative merge, split_coop, and soft-real-time update.
- `enum bfqq_expiration` lists expiration reasons: too idle, budget timeout, budget exhausted, no more requests, preempted.
- Prototypes connect BFQ components: queue lookup, weights tree operations, expiration, queue put/ref release, dispatch scheduling, async queues, cgroup updates, entity initialization, hierarchical WF2Q operations, queue activation/deactivation, busy accounting, and pending-group accounting.

Logging:
- `bfq_bfqq_name()` formats queue names for trace messages.
- `bfq_log_bfqq()` emits cgroup-aware trace messages when group scheduling is enabled, otherwise plain block trace messages.
- `bfq_log()` emits scheduler-level trace messages.

This header is the type contract for `bfq-cgroup.c`, `bfq-wf2q.c`, and the main BFQ scheduler implementation.
