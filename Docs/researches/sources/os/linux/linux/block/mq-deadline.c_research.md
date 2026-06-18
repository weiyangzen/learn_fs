# File Research: sources/os/linux/linux/block/mq-deadline.c

Implements the multi-queue deadline I/O scheduler, adapting classic deadline scheduling to blk-mq with I/O priority classes.

Key responsibilities:
- Maintains per-priority read/write RB trees ordered by sector and FIFO lists ordered by expiration.
- Supports realtime, best-effort, and idle I/O priority classes.
- Prefers reads but limits write starvation through `writes_starved`.
- Batches sequential requests with `fifo_batch`.
- Ages lower-priority requests through `prio_aging_expire`.
- Supports front/back merge through elevator hash and RB-tree lookup.

Important structures:
- `struct deadline_data` stores global scheduler state, dispatch list, tunables, and lock.
- `struct dd_per_prio` stores per-priority sort lists, FIFO lists, latest positions, and stats.
- `struct io_stats_per_prio` tracks inserted, merged, dispatched, and completed counts.

Important functions:
- `dd_dispatch_request()` selects the next request across dispatch list, aged lower-priority work, and priority order.
- `__dd_dispatch_request()` implements core deadline read/write selection.
- `dd_insert_requests()` / `dd_insert_request()` place requests into FIFO/RB/hash state.
- `dd_request_merge()`, `dd_bio_merge()`, `dd_merged_requests()` implement scheduler merging.
- `dd_finish_request()` updates completion stats.
- `dd_init_sched()` / `dd_exit_sched()` allocate and validate scheduler state.

Interfaces:
- Sysfs exposes `read_expire`, `write_expire`, `writes_starved`, `front_merges`, `fifo_batch`, and `prio_aging_expire`.
- Debugfs exposes priority/direction FIFO lists, next request, dispatch list, queued counts, and owned-by-driver counts.
- Registers as `"mq-deadline"` with alias `"deadline"`.

Research relevance:
- This is the default elevator selected by `elevator_set_default()` for single-queue/shared-tag devices.
