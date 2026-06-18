# sources/test-tools/stress-ng/stress-handle.c

## Purpose
`stress-handle.c` exercises Linux file-handle APIs by resolving `/dev/zero` with `name_to_handle_at()`, reopening it through `open_by_handle_at()`, and issuing valid and invalid handle operations.

## Important APIs, Types, And Functions
`stress_mount_info_t` stores parsed mount path and mount id pairs from `/proc/self/mountinfo`. `get_mount_info()` fills a fixed `MAX_MOUNT_IDS` array using `getline()` and `sscanf()`, and `free_mount_info()` releases duplicated paths. `stress_handle_child()` allocates and resizes `struct file_handle`, calls `name_to_handle_at()` first to discover handle size and then to fetch the handle, finds the matching mount fd, calls `open_by_handle_at()`, and exercises malformed flags, names, sizes, fds, and stale randomized handles. `stress_handle()` wraps the child in `stress_oomable_child()`.

## Control Flow
The parent parses mountinfo, waits at the sync barrier, and runs an OOM-isolated child. The child loops until `stress_continue()` is false: allocate file handle, request size expecting `EOVERFLOW`, resize, fetch handle, open the mount path for the returned mount id, try `open_by_handle_at()`, run negative syscall coverage, close descriptors, free memory, and increment bogo ops.

## State And Persistence
State is a static mount-info array and per-iteration heap allocations/fds. The file under test is `/dev/zero`; no files are created or persisted. Mount information is a snapshot from `/proc/self/mountinfo`.

## Dependencies And Integration Points
Feature gates require `name_to_handle_at`, `open_by_handle_at`, and `AT_FDCWD`. It uses stress-ng bad-fd generation, OOM isolation, sync, process state, and logging helpers.

## Risks
`open_by_handle_at()` commonly requires privilege and may return `EPERM`, which is intentionally nonfatal. Mountinfo parsing assumes stable field positions and unescaped paths. Mount topology can change between parsing and use. Allocation failures are tolerated by retrying.

## Test Signals
Expected signals are `EOVERFLOW` on the sizing call, graceful skip on `ENOSYS`, tolerated `EPERM`, no leaked fds across iterations, correct mount id lookup, and successful cleanup of mount path allocations.
