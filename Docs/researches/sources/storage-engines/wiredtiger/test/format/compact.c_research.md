# sources/storage-engines/wiredtiger/test/format/compact.c

## Purpose
`compact.c` provides foreground and background compaction workers for format. It exercises `WT_SESSION::compact` on selected tables and repeatedly toggles the background compaction server.

## Important APIs, Types, And Functions
The file exports `WT_THREAD_RET background_compact(void *)` and `WT_THREAD_RET compact(void *)`. It uses `session->compact`, `table_select`, `wt_wrap_open_session`, `mmrand`, `GV(BACKGROUND_COMPACT_FREE_SPACE_TARGET)`, and `GV(COMPACT_FREE_SPACE_TARGET)`.

## Control Flow
`background_compact` starts shortly after run start, then every ten minutes randomly enables or disables background compaction with a configured free-space target. On shutdown it always attempts to disable background compaction. `compact` starts within 15 seconds, then every 23 seconds chooses a table and runs foreground compaction with `free_space_target`.

## State And Persistence Behavior
Both workers affect WiredTiger file layout and free-space reclamation. They do not modify logical records or format config files. Background compaction also changes connection-level compaction server state and is explicitly disabled during teardown.

## Dependencies And Integration Points
Compaction is enabled or disabled by `format_config.c` based on in-memory, tiered, and disaggregated storage constraints. Foreground compaction collides naturally with checkpoints, alter, eviction, and workload writes. Background compaction state is also tracked conceptually by global format configuration.

## Risks And Test Signals
Expected return codes include `EBUSY` for races, `ETIMEDOUT` for long compactions, `WT_CACHE_FULL`, and `WT_ROLLBACK`. Unexpected return codes are assertion failures. Risks are enabling compaction for unsupported storage modes, failing to disable the background server, and treating normal contention as fatal.
