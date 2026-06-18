<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/freebsd/mntent_compat.c -->
# sources/user-network-fs/nfs-ganesha/src/os/freebsd/mntent_compat.c

## Purpose
This file provides Linux-style mount-entry helpers on FreeBSD, adapting `getmntinfo()`/`statfs` data to `struct mntent` and implementing `hasmntopt()`.

## Important APIs, Types, and Functions
Global static state includes `pos`, `mntsize`, `_mntbuf`, and `_mntent`. `mntoptions[]` maps FreeBSD mount flags to option strings. `hasmntopt()` searches a mount option string for a named option. `catopt()` appends an option to a buffer. `flags2opts()` converts mount flags to `ro`/`rw` plus named options. `statfs_to_mntent()` fills the static `_mntent`. `getmntent(FILE *fp)` iterates mounted filesystems from `getmntinfo()`.

## Control Flow
`getmntent()` lazily calls `getmntinfo()` when iteration is reset, logs all mount source names at full debug, increments `pos`, returns `NULL` and resets when all entries are consumed, otherwise returns a static `struct mntent` view for the current `statfs`. `hasmntopt()` duplicates the options string, tokenizes by spaces, and returns a pointer into the original string when a match is found.

## State and Persistence Behavior
Iteration state is global and not thread-safe. Returned `struct mntent` and option buffer are static and overwritten by subsequent calls. No persistent files are modified.

## Dependencies and Integration Points
The file depends on `os/freebsd/mntent.h`, FreeBSD `getmntinfo()`/`statfs`, mount flag constants, Ganesha memory wrappers, and logging. It supports FSAL code that includes the generic `os/mntent.h`.

## Risks and Edge Cases
`flags2opts()` initializes `char *res = NULL` and passes it to `catopt()` instead of the provided `buf`; this appears to dereference a null pointer when options are appended. `hasmntopt()` tokenizes with `strtok()`, which is not thread-safe. The `FILE *fp` argument to `getmntent()` is ignored. The static iteration state prevents concurrent or nested mount iteration.

## Test Signals
FreeBSD tests should call `getmntent()` through a full mount table, verify option strings for representative flags, call `hasmntopt()` for present/absent options, and run under sanitizers to catch the apparent null-buffer bug in `flags2opts()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/freebsd/mntent_compat.c -->
