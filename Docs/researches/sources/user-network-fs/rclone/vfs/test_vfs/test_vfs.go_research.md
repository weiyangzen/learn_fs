<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/test_vfs/test_vfs.go -->
# sources/user-network-fs/rclone/vfs/test_vfs/test_vfs.go

## Purpose
Standalone stress tool for a mounted VFS directory. It randomly creates, opens, reads, writes, renames, lists, and removes files or directories to expose deadlocks and state inconsistencies.

## Important APIs, Types, and Functions
Defines command-line flags for name length, verbosity, worker count, iterations, and timeout; `Test` state; `NewTest`; operation methods `list`, `rename`, `open`, `close`, `read`, `write`, `remove`, `mkdir`, `rmdir`; `Tidy`; `RandomTests`; and `main`.

## Control Flow
`main` creates the target directory, starts multiple goroutines, and each goroutine creates a `Test` that randomly chooses file or directory operations for a configured number of iterations. A per-test timer is reset before each operation and signals a deadlock if no progress occurs within the timeout.

## State and Persistence Behavior
Mutates the mounted filesystem directly via `os` and `rclone/lib/file`. Each `Test` tracks current name, created state, optional open handle, file-vs-dir mode, and timeout timer. `Tidy` closes and removes any remaining test path.

## Dependencies and Integration Points
Uses standard OS filesystem calls against an already mounted VFS, plus rclone logging, random name generation, and file wrappers. It is not part of normal package tests and is intended as an external harness.

## Risks and Edge Cases
The tool reports errors but generally continues; it is stochastic, so failures may be non-reproducible without logging. Directory and file operations are isolated per random name, so it stresses handle/lifecycle behavior more than shared-path write conflicts. `kick` drains timer channels and must be used carefully to avoid timer races.

## Test Signals
Useful manual signal for deadlocks under concurrent mixed operations on real mounts. It complements unit tests by exercising actual OS/mount interactions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/test_vfs/test_vfs.go -->
