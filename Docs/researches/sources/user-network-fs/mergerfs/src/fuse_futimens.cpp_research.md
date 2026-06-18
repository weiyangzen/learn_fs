# sources/user-network-fs/mergerfs/src/fuse_futimens.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_futimens.cpp` implements timestamp updates by open file handle. The source was read as a complete 62-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::futimens`, `FileInfo`, `fs::futimens`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::futimens` resolves `FileInfo` and delegates to `fs::futimens` with the supplied timespec array.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_futimens.hpp", "errno.hpp", "fileinfo.hpp", "fs_futimens.hpp", "state.hpp", "fuse.h", <sys/stat.h>. Timestamp semantics depend on platform futimens support and UTIME_NOW/OMIT handling below the wrapper.

## Risks and Edge Cases

Timestamp semantics depend on platform futimens support and UTIME_NOW/OMIT handling below the wrapper.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
