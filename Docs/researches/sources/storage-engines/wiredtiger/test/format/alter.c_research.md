# sources/storage-engines/wiredtiger/test/format/alter.c

## Purpose
`alter.c` supplies the format-test worker that periodically calls `WT_SESSION::alter` on a randomly selected table. Its only mutated metadata is `access_pattern_hint`, alternating between `none` and `random`, so it stresses metadata alter paths without changing cache-residency settings that could make eviction impossible in small-cache runs.

## Important APIs, Types, And Functions
The file exports `WT_THREAD_RET alter(void *)`, declared in `format.h` and launched as an auxiliary worker when `ops.alter` is enabled. It uses `SAP` for session event-handler private data, `TABLE` from the global table array, `g.wts_conn`, `g.extra_rnd`, `g.workers_finished`, and helpers `wt_wrap_open_session`, `wt_wrap_close_session`, `mmrand`, `table_select`, and `trace_msg`.

## Control Flow
The thread opens a WiredTiger session, then loops until `g.workers_finished`. Each iteration chooses a 1-10 second period, builds an alter config string, toggles the next value, selects a table using non-data RNG selection, traces start/stop, and retries while the return is nonzero and not `EBUSY`. After the attempt, it sleeps in one-second increments so shutdown is responsive.

## State And Persistence Behavior
The state change is persisted in WiredTiger metadata for the chosen object through `session->alter`. The thread keeps only local counters and the next access-hint boolean. It does not write format config files or data records.

## Dependencies And Integration Points
It depends on the shared `format.h` globals, inline RNG/table helpers, and WiredTiger metadata API. Backup/checkpoint/compact threads may race with this metadata operation, and `EBUSY` is treated as an expected collision signal rather than a test failure.

## Risks And Test Signals
The main risk is broadening alter settings to options with stronger cache or data-format effects; the current code intentionally avoids cache-resident toggles. Useful signals are trace lines for alter start/stop, frequent `EBUSY` under metadata pressure, and the absence of fatal `session.alter` errors.
