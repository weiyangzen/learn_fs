# sources/user-network-fs/mergerfs/src/fs_wait_for_mount.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_wait_for_mount.cpp` waits for branch paths to become mounted and optionally triggers mounts. The source was read as a complete 171-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `wait_for_mount`, `fs::mount`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`wait_for_mount` detects marker xattrs/files or device-number changes, calls `fs::mount` for unready targets, polls until timeout, and logs readiness.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_wait_for_mount.hpp", "syslog.hpp", "fs_mount.hpp", "fs_exists.hpp", "fs_lgetxattr.hpp", "fs_lstat.hpp", "fs_stat.hpp", <functional>. Used during startup for branch readiness. Marker semantics and timeout tuning are operational risks.

## Risks and Edge Cases

Used during startup for branch readiness. Marker semantics and timeout tuning are operational risks.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
