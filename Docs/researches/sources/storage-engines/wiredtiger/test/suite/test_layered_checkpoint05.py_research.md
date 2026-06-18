# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint05.py

Purpose: tests creating an empty layered table while a slow precise checkpoint is already running, then verifies the table is visible and empty to a follower and after restart.

Important APIs/types/functions: class extends `checkpoint_util` and uses `wait_for_checkpoint_start`, `wtthread.Thread`, `timing_stress_for_test=[checkpoint_slow]`, `precise_checkpoint=true`, `restart_without_local_files(step_up=True)`, `disagg_advance_checkpoint`, and standard session create/checkpoint/cursor APIs.

Control flow: the connection starts as follower, steps up to leader, sets stable timestamp 1, creates and populates a separate table, and starts checkpointing in a background thread. Once checkpoint start is detected, the main session creates the empty target table and waits for checkpoint completion. It disables timing stress, takes another checkpoint, opens a follower and advances it, then scans the new table expecting zero rows. It restarts without local files as leader and checks the table remains present and empty.

State and persistence behavior: validates metadata persistence for a concurrently created empty layered table, including shared checkpoint pickup and local-file reconstruction. The important state is table existence rather than row contents.

Dependencies/integration points: integrates checkpoint utility timing detection, disaggregated role reconfiguration, follower checkpoint pickup, and restart-without-local-files helper behavior.

Risks: timing-stress dependence can make the test sensitive to checkpoint scheduling; the short post-start sleep assumes the checkpoint is sufficiently in progress. It also depends on precise checkpoint timestamp setup.

Test signals: pass means concurrent table create is synchronized with checkpoint metadata and survives follower pickup and leader restart without local files.
