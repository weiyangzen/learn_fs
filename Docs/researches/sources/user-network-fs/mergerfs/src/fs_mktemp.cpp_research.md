# sources/user-network-fs/mergerfs/src/fs_mktemp.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_mktemp.cpp` creates hidden temporary files beside a target path. The source was read as a complete 101-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `mktemp_in_dir`, `.name_random`, `_PC_NAME_MAX`, `O_CREAT|O_EXCL`, `EEXIST`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`mktemp_in_dir` generates `.name_random` candidates bounded by `_PC_NAME_MAX`, opens with `O_CREAT|O_EXCL`, retries on `EEXIST`, and returns fd plus path.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_mktemp.hpp", "errno.hpp", "fs_open.hpp", "fs_path.hpp", "rnd.hpp", <limits.h>, <unistd.h>, <algorithm>. Used by write/copy/replace flows needing same-directory temp files. Risks are random collision after limited retries and filename truncation.

## Risks and Edge Cases

Used by write/copy/replace flows needing same-directory temp files. Risks are random collision after limited retries and filename truncation.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
