# sources/user-network-fs/mergerfs/src/fuse_chmod.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_chmod.cpp` applies chmod across policy-selected branch instances of a pooled path. The source was read as a complete 118-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::chmod`, `fs::lchmod`, `PolicyRV`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::chmod` runs `fs::lchmod` for each action branch, records successes/errors in `PolicyRV`, and reports the error relevant to the active getattr branch after partial success.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_chmod.hpp", "config.hpp", "errno.hpp", "fs_lchmod.hpp", "fs_path.hpp", "policy_rv.hpp", "fuse.h", <cstring>. Partial success can leave branch metadata divergent.

## Risks and Edge Cases

Partial success can leave branch metadata divergent.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
