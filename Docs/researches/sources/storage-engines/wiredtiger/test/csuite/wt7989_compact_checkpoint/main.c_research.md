# sources/storage-engines/wiredtiger/test/csuite/wt7989_compact_checkpoint/main.c

## Purpose
WT-7989 verifies that compaction and checkpoint can overlap without preventing compaction progress or leaving excessive reusable space. It runs stress and synchronized cases for row-store and column-store tables.

## Important APIs, Types, and Functions
- Uses `WT_CONNECTION`, `WT_SESSION`, pthreads, data-source statistics cursors, and timing stress.
- `run_test_clean` creates separate suffixed homes for stress/normal row/column cases.
- `populate` inserts one million records with large string payloads.
- `remove_records` deletes the middle third to create compactable space.
- `thread_func_compact` runs `session->compact`.
- `thread_func_checkpoint` runs three checkpoints with random sleeps.
- `thread_wait` synchronizes compact/checkpoint start in non-stress cases using an atomic counter.
- `get_compact_progress` and `check_db_size` assert compact stats and reusable-space percentage.

## Control Flow
`main` runs four scenarios: slow-checkpoint row, synchronized row, slow-checkpoint column, synchronized column. Each scenario recreates its home, opens a 2 GiB cache connection, optionally sets `WT_TIMING_STRESS_CHECKPOINT_SLOW` directly in the connection implementation, creates/populates/checkpoints a table, deletes one third of records, starts compact and checkpoint threads, waits for both, reads compact progress stats, checks file-size reuse percentage, and closes.

## State and Persistence Behavior
Each scenario persists a large table with one million records, then durable deletes and compaction rewrites blocks. Statistics counters for compact pages reviewed/skipped/rewritten and block reuse bytes are the main postcondition data.

## Dependencies and Integration Points
The test uses internal `WT_CONNECTION_IMPL` timing-stress flags, pthreads, statistics constants such as `WT_STAT_DSRC_BTREE_COMPACT_PAGES_REVIEWED`, and `TEST_OPTS` homes/URI. It is resource-heavy due to 2 GiB cache and large table volume.

## Risks and Test Signals
Assertions require pages reviewed and rewritten to be nonzero, and reusable space after compaction to be at most 20%. Timing and random checkpoint sleeps can make runtime variable. The test assumes compaction can make measurable progress after deleting the middle third.
