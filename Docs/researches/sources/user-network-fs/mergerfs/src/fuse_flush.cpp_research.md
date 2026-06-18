# sources/user-network-fs/mergerfs/src/fuse_flush.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_flush.cpp` implements FUSE flush using the close-of-dup pattern. The source was read as a complete 61-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::flush`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::flush` duplicates the backing fd and closes the duplicate so close-time writeback errors can surface without closing the real handle.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_flush.hpp", "errno.hpp", "fileinfo.hpp", "fs_close.hpp", "fs_dup.hpp", "state.hpp", "fuse.h". Returns `-EIO` if dup fails; otherwise errors mirror close on the duplicate.

## Risks and Edge Cases

Returns `-EIO` if dup fails; otherwise errors mirror close on the duplicate.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
