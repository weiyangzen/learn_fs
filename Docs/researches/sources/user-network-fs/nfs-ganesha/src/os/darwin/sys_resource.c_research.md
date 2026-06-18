<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/darwin/sys_resource.c -->
# sources/user-network-fs/nfs-ganesha/src/os/darwin/sys_resource.c

## Purpose
This Darwin-specific file wraps open-file resource limit discovery and normalizes macOS `RLIMIT_NOFILE` semantics for Ganesha.

## Important APIs, Types, and Functions
It implements `get_open_file_limit(struct rlimit *rlim)`. The function calls `getrlimit(RLIMIT_NOFILE, rlim)` and clamps `rlim->rlim_max` to `OPEN_MAX` when the reported hard limit exceeds `OPEN_MAX`.

## Control Flow
The function returns `-1` if `getrlimit()` fails. On success it applies the macOS compatibility clamp and returns zero.

## State and Persistence Behavior
No persistent state is modified. The caller-provided `struct rlimit` is filled and possibly adjusted.

## Dependencies and Integration Points
It depends on `sys_resource.h`, `getrlimit()`, `RLIMIT_NOFILE`, and Darwin `OPEN_MAX` from `sys/syslimits.h`. It integrates with code that sizes file descriptor resources during startup.

## Risks and Edge Cases
The clamp is Darwin-specific and intentionally deviates from raw `getrlimit()` output. If callers expect the kernel-reported hard limit rather than a usable maximum, they may see a lower value. Failure handling leaves `errno` from `getrlimit()`.

## Test Signals
Darwin tests should verify success on normal systems, error propagation for invalid calls if mockable, and clamping when a hard limit greater than `OPEN_MAX` is reported.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/darwin/sys_resource.c -->
