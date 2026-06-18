<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/compact.h -->
# sources/storage-engines/wiredtiger/src/include/compact.h

## Purpose
Defines the small state object used by WiredTiger compaction operations. It records whether the run is estimation-only, how many files have been considered, the target amount of reclaimable space, the configured time limit, and progress timestamps.

## Important APIs, Types, and Functions
`WT_COMPACT_STATE` contains `dryrun`, `file_count`, `free_space_target`, `max_time`, `begin`, and `last_progress`. There are no inline functions or macros beyond the struct definition.

## Control Flow
Runtime compaction code initializes this structure at the start of a compact operation, updates `file_count` as files are inspected or processed, checks elapsed time against `begin` and `max_time`, compares estimated or actual free space against `free_space_target`, and uses `last_progress` to rate-limit progress messages.

## State and Persistence Behavior
The struct is transient operation state. It does not persist data directly, but it guides compaction decisions that may rewrite files and release disk space. In dry-run mode, callers should use it to estimate without performing the rewriting phase.

## Dependencies and Integration Points
Depends only on standard `bool`, integer types, and `struct timespec`. It integrates with compaction command execution, file iteration, progress logging, timeout enforcement, and free-space estimation/recovery logic elsewhere in WiredTiger.

## Risks and Edge Cases
Timeout checks depend on monotonic and consistent time handling by callers. `free_space_target` and dry-run behavior must be interpreted consistently so dry runs do not mutate files. Progress timestamps should be initialized before logging decisions. Large compactions need `file_count` and time accounting to remain accurate across many files.

## Test Signals
Relevant tests include compact dry-run behavior, compact timeout/max-time enforcement, free-space target handling, progress message throttling, and multi-file compact runs that update `file_count`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/compact.h -->
