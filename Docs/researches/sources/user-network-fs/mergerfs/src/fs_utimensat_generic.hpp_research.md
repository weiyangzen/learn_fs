# sources/user-network-fs/mergerfs/src/fs_utimensat_generic.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_utimensat_generic.hpp` implements a generic utimensat/futimens fallback using older timeval APIs. The source was read as a complete 294-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `UTIME_NOW`, `UTIME_OMIT`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

Validates flags and timespec values, handles `UTIME_NOW`/`UTIME_OMIT`, reads current timestamps when needed, and delegates through fstatat/futimesat/lutimens helpers.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_fstat.hpp", "fs_fstatat.hpp", "fs_futimesat.hpp", "fs_lutimens.hpp", "fs_stat_utils.hpp", <string>, <fcntl.h>, <sys/stat.h>. High-risk portability code: subtle conversion bugs can change timestamps unexpectedly.

## Risks and Edge Cases

High-risk portability code: subtle conversion bugs can change timestamps unexpectedly.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
