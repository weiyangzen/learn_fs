<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/pool.go -->
# sources/user-network-fs/go-fuse/splice/pool.go

## Purpose
Provides the global pool for reusable Linux splice pipe pairs.

## Important APIs, Types, and Functions
Public helpers are `ClearSplicePool`, `Get`, `Done`, `Drop`, `Total`, and `Used`; internal methods manage `unused` and `usedCount`.

## Control Flow
`get` increments used count and returns an unused pair or creates a new one. `done` drains the pipe and stores it for reuse. `drop` closes it and decrements usage.

## State and Persistence Behavior
Pool state is process-global and protected by a mutex; unused pairs retain open fds until cleared or process exit.

## Dependencies and Integration Points
Used by `CopyFds` and other go-fuse splice users.

## Risks and Edge Cases
Misbalanced `Get`/`Done`/`Drop` calls leak counts or fds. `done` drains before locking, so callers must not use the pair concurrently.

## Test Signals
Pool tests and fd-leak tests are useful signals; race tests should stress concurrent get/done/drop.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/pool.go -->
