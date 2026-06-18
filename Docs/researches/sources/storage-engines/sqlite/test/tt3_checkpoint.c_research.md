## sources/storage-engines/sqlite/test/tt3_checkpoint.c

### Purpose
`tt3_checkpoint.c` adds checkpoint starvation scenarios to `threadtest3`. It compares passive and restart WAL checkpoints while long-lived readers repeatedly hold snapshots.

### Important APIs, types, and functions
`CheckpointStarvationCtx` stores checkpoint mode and peak frame count. `checkpoint_starvation_walhook()` is registered with `sqlite3_wal_hook()` and invokes `sqlite3_wal_checkpoint_v2()` when the WAL reaches `CHECKPOINT_STARVATION_FRAMELIMIT`. `checkpoint_starvation_reader()` checks snapshot isolation during 100 ms read transactions. `checkpoint_starvation_main()` runs the shared setup. `checkpoint_starvation_1()` and `_2()` assert expected WAL growth behavior.

### Control flow
The main helper creates `test.db` in WAL mode, launches four staggered readers, installs the WAL hook on the writer connection, and inserts random blobs until timeout. It prints checkpoint mode, peak WAL frames, and transaction count, then joins readers. The passive variant expects large WAL growth; the restart variant expects the WAL to stay near the frame limit.

### State and persistence behavior
All activity is in `test.db` and its WAL file. Readers hold transactions open across sleeps, preserving snapshots. The writer appends rows and performs hook-driven checkpoints.

### Dependencies and integration points
This file relies on `threadtest3.c` infrastructure, SQLite WAL hooks, WAL checkpoint APIs, and shared `Error`, `Sqlite`, and `Threadset` types. It is included into `threadtest3.c`, not compiled alone.

### Risks and test signals
The assertions depend on scheduler timing and filesystem speed; slow or unusual environments can alter frame growth. Signals are no reader isolation failures, printed peak WAL frames, transaction count, and explicit errors if passive WAL does not grow or restart WAL grows too large.
