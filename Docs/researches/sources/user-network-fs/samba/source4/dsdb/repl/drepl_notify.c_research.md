# sources/user-network-fs/samba/source4/dsdb/repl/drepl_notify.c

Purpose: implements outbound replication notifications. It detects when local partitions have new USNs and sends remote `DsReplicaSync` calls so partners pull changes from this DC.

Important APIs/functions: `dreplsrv_notify_schedule()` manages the notify timer; `dreplsrv_notify_check_all()` scans partitions; `dreplsrv_notify_check()` compares partition `uSNHighest`/`uSNUrgent` with per-source `notify_uSN`; `dreplsrv_schedule_notify_sync()` queues deduplicated notify operations; `dreplsrv_notify_run_ops()` runs one active notify; `dreplsrv_op_notify_send()` connects/binds, sends `DsReplicaSync`, and `dreplsrv_notify_op_callback()` updates status.

Control flow/state: timer run allocates a scratch context, queues notifications from `repsTo`, and calls `dreplsrv_run_pending_ops()`. Notify operations share the DREPL single-operation lane with pull operations. On success, the in-memory `notify_uSN` is advanced and `drepl_reps_update()` writes status timestamps/failure counts to `repsTo`; on failure, only status is updated. RODCs do not schedule notify service startup.

Dependencies/integration: outgoing DRSUAPI helper, partition/source lists, `dsdb_loadreps()`, `dsdb_load_partition_usn()`, `drepl_out_pull.c` status updater, and DRSUAPI RPC. Risks include starvation behind pull operations, notification dedupe missing changed flags, and typo-level maintainability (`huger` comment). Test signals: urgent flag when `notify_uSN < uSNUrgent`, no notify for unchanged USNs, status persistence in `repsTo`, RODC startup skip, and remote `DsReplicaSync` request fields.
