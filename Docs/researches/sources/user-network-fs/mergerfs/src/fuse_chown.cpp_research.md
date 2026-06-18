# sources/user-network-fs/mergerfs/src/fuse_chown.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_chown.cpp` applies owner/group changes across policy-selected branch instances. The source was read as a complete 115-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::chown`, `fs::lchown`, `PolicyRV`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::chown` runs `fs::lchown` on each action branch and uses `PolicyRV` to collapse partial errors relative to the active branch.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_chown.hpp", "config.hpp", "errno.hpp", "fs_lchown.hpp", "fs_path.hpp", "policy_rv.hpp", "fuse.h", <string>. Branch divergence is possible when only some underlying files accept chown.

## Risks and Edge Cases

Branch divergence is possible when only some underlying files accept chown.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
