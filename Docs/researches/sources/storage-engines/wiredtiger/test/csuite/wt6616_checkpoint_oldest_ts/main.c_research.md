# sources/storage-engines/wiredtiger/test/csuite/wt6616_checkpoint_oldest_ts/main.c

## Purpose
WT-6616 validates recovery correctness for timestamped checkpoints after an unclean shutdown. A child workload inserts and deletes timestamped keys while checkpointing; the parent kills it, runs recovery, and verifies every key from recovered oldest to stable timestamp is visible at its own timestamp.

## Important APIs, Types, and Functions
- Uses `fork`, `kill(SIGKILL)`, `waitpid`, `sigaction`, pthread helpers, timestamps, sentinel files, and recovery config.
- `thread_ckpt_run` repeatedly runs `checkpoint(use_timestamp=true)`, queries `last_checkpoint`, and creates `checkpoint_done` after a checkpoint newer than `MAX_DATA`.
- `thread_run` inserts key X at timestamp X, advances stable to X, deletes at X+1, and advances oldest once data exceeds `MAX_DATA`.
- `run_workload` opens the child database, creates a non-logged table, and starts checkpoint and worker threads.
- Parent `main` waits for sentinel, sleeps a randomized or specified timeout, kills child, opens recovery, queries stable/oldest, and checks visibility.

## Control Flow
The program parses options for column-store mode, home, preserve, and timeout. Parent creates a clean home and forks. Child changes into the home, opens WiredTiger with logging enabled globally but creates the test table with `log=(enabled=false)`, starts checkpoint and worker threads, and waits forever. Parent waits for the first qualifying checkpoint, sleeps, kills the child, changes into the home, copies data for debugging, opens recovery, and scans timestamps from oldest through stable, starting a read-timestamp transaction for each.

## State and Persistence Behavior
The durable table is explicitly non-logged so timestamped history after recovery is meaningful. Stable and oldest timestamps are part of the persisted checkpoint state. The sentinel file coordinates parent timing. The parent may clean test artifacts and remove the home after verification.

## Dependencies and Integration Points
The test depends on process control, timestamped checkpoints, non-logged table recovery semantics, `testutil_copy_data`, and `TESTUTIL_ENV_CONFIG_REC`. The smoke wrapper runs row and column variants.

## Risks and Test Signals
Missing keys between oldest and stable after recovery signal data loss. A child exit before being killed is fatal. In `thread_run`, the remove path always calls `cursor->set_key(cursor, kname)` even when `use_columns` is true, unlike insertion and verification; that asymmetry is a notable column-mode risk. Runtime is timing-dependent and randomized unless `-t` is supplied.
