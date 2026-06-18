# sources/user-network-fs/samba/source4/dsdb/repl/drepl_out_pull.c

Purpose: scheduling and queue execution for outbound pull replication operations.

Important APIs/functions: `drepl_reps_update()` updates `repsFrom` or `repsTo` status timestamps, result code, and consecutive failure counters; `dreplsrv_schedule_partition_pull_source()` creates a pending pull operation; `dreplsrv_schedule_pull_replication()` schedules all partition sources; `dreplsrv_run_pull_ops()` starts the next pull; `dreplsrv_pending_op_callback()` receives completion and invokes optional extended-op callbacks.

Control flow/state: periodic code enqueues all sources, IRPC/exop paths enqueue specific sources, and `dreplsrv_run_pull_ops()` enforces one active pull/notify at a time. Before starting, it records `last_attempt` and checks local inbound replication disablement unless forced. Success/failure status is persisted through `dsdb_savereps()` for normal pulls; extended operations skip normal `repsFrom` status persistence and report through callbacks.

Dependencies/integration: DLIST queues in `dreplsrv_service`, outgoing helper send/recv, SAMDB NTDS options, DSDB reps blob load/save, and notify queue interlock. Risks include duplicate scheduled pulls, a failure path that invokes callbacks without freeing `op` in the visible code path, disabled inbound replication blocking non-forced requests, and status-only persistence separate from high-watermark commit. Test signals: queue order, forced vs disabled inbound replication, callback completion for sync IRPC/exops, and `repsFrom` status field updates after failure/success.
