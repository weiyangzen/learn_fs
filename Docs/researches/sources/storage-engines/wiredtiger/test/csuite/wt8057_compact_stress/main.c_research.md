# sources/storage-engines/wiredtiger/test/csuite/wt8057_compact_stress/main.c

## Purpose
WT-8057 validates data consistency if compact is interrupted by an unclean shutdown. A child repeatedly mutates two identical tables while compacting only one; the parent kills the child and verifies both tables match after recovery.

## Important APIs, Types, and Functions
- Uses `fork`, `SIGKILL`, `sigaction`, `WT_EVENT_HANDLER`, compact event callbacks, statistics cursors, and recovery open.
- `handle_general` handles `WT_EVENT_COMPACT_CHECK` and periodically returns an error to interrupt compact.
- `workload_compact` creates two tables, populates both identically, checkpoints, removes identical key ranges, compacts `uri1`, logs compact stats, repopulates deleted records, and repeats.
- `verify_tables` and `verify_tables_helper` compare both directions across `table:compact1` and `table:compact2`.
- `log_db_size` and `get_compact_progress` report compaction behavior.

## Control Flow
`main` runs row and column tests. For each, parent creates a work directory and forks. The child opens WiredTiger, creates both tables, populates 100,000 records, enters up to 40 mutation/compact loops, and creates `checkpoint_done` after the first checkpoint. Parent waits for the sentinel, sleeps 40 seconds, kills the child, reopens the home with the same event handler and connection config, and verifies table equality.

## State and Persistence Behavior
Two tables are maintained as logical mirrors. Only the first is compacted, so recovery must preserve logical equality despite interrupted compaction and possible event-handler compact interruptions. The sentinel file gates parent timing.

## Dependencies and Integration Points
The test depends on process control, compact event callbacks, statistics, recovery, and row/column table configs. It integrates with the general event handler path through `WT_EVENT_COMPACT_CHECK`.

## Risks and Test Signals
Data mismatch, missing keys, child premature exit, or compact callback behavior not surfacing as an error when requested are failures. The child is expected not to finish naturally. The test is time- and IO-heavy.
