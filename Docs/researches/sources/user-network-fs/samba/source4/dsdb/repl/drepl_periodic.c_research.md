# sources/user-network-fs/samba/source4/dsdb/repl/drepl_periodic.c

Purpose: periodic scheduler for DREPL pull replication and RID allocation checks, plus the dispatcher for pending pull/notify operations.

Important APIs/functions: `dreplsrv_periodic_schedule()` manages the timer; `dreplsrv_periodic_run()` refreshes partitions, queues pull replication, checks RID pool needs, and runs the operation queue; `dreplsrv_run_pending_ops()` chooses between notify and pull queues; `dreplsrv_pendingops_schedule_pull_now()` schedules an immediate pull dispatch after manual `DsReplicaSync`.

Control flow/state: like KCC timers, zero intervals are coerced to one second and rescheduling avoids moving an existing timer later. Each periodic run refreshes topology first because KCC/admin tools may have changed `repsFrom`/`repsTo`, then schedules all source pulls and processes one operation. The dispatcher favors whichever pending notify/pull has the older `schedule_time`, with only one active op in the shared lane.

Dependencies/integration: tevent timers/immediates, partition refresh, pull scheduler, RID allocation, and notify/pull run functions. Risks include queue growth if periodic scheduling enqueues duplicates faster than they drain, single-lane throughput limits, ignored refresh/schedule errors in the visible periodic body, and timer termination on schedule failure. Test signals: interval handling, immediate pull from `DsReplicaSync`, operation ordering by `schedule_time`, and refresh before scheduling after topology changes.
