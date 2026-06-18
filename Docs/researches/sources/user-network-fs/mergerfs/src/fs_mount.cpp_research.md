# sources/user-network-fs/mergerfs/src/fs_mount.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_mount.cpp` mounts a target by invoking the system `mount` helper. The source was read as a complete 28-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::mount(target)`, `mount <target>`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`fs::mount(target)` builds a subprocess command equivalent to `mount <target>` and returns the subprocess result.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_mount.hpp", "subprocess/subprocess.hpp". Used by mount-wait startup logic. It depends on system mount configuration and helper permissions.

## Risks and Edge Cases

Used by mount-wait startup logic. It depends on system mount configuration and helper permissions.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
