# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint06.py

Purpose: verifies disaggregated role changes are synchronized with checkpointing so a checkpoint cannot partly complete as leader and partly as follower.

Important APIs/types/functions: extends `checkpoint_util`; uses `restart_without_local_files`, `wtthread.Thread`, `wait_for_checkpoint_start`, `timing_stress_for_test=[checkpoint_slow]`, role `reconfigure`, `disagg_get_complete_checkpoint_ext`, and timestamped transactions.

Control flow: it starts as follower, steps up to leader, creates data at timestamp 1, checkpoints, then restarts as follower. In part 1 it writes timestamp 2 data while follower, sets stable timestamp 2, steps up, verifies the latest disagg checkpoint is still timestamp 1, then checkpoints and expects timestamp 2. In part 2 it writes timestamp 3 data as leader, starts a slow checkpoint in another thread, waits for it to start, steps down to follower while checkpointing, joins, disables stress, and verifies the checkpoint timestamp is 3. After restart it reads all three values.

State and persistence behavior: state is role, stable timestamp, checkpoint timestamp, and durable table values across local-file restart. The checkpoint should preserve the role captured at checkpoint start.

Dependencies/integration points: exercises connection reconfiguration, checkpoint publication, recovery without local files, timing stress, and disaggregated role transition synchronization.

Risks: concurrent role change timing is central; if wait detection is imprecise the test may miss the target interleaving. It also assumes checkpoint timestamp is a sufficient proxy for whether a disagg checkpoint was published.

Test signals: pass indicates step-up does not retroactively publish a follower checkpoint and step-down does not invalidate an in-flight leader checkpoint.
