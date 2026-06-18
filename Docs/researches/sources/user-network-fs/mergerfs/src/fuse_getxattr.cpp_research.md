# sources/user-network-fs/mergerfs/src/fuse_getxattr.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_getxattr.cpp` implements FUSE getxattr including mergerfs virtual attributes. The source was read as a complete 205-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::getxattr`, `security.capability`, `user.mergerfs.*`, `lgetxattr`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::getxattr` handles control-file config xattrs, optional `security.capability` hiding, xattr mode, virtual `user.mergerfs.*` values, and fallback `lgetxattr`.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_getxattr.hpp", "config.hpp", "errno.hpp", "fs_findallfiles.hpp", "fs_lgetxattr.hpp", "fs_path.hpp", "fs_statvfs_cache.hpp", "str.hpp". Exposes configuration and branch paths intentionally. Buffer-size handling follows xattr probe conventions and can return `-ERANGE`.

## Risks and Edge Cases

Exposes configuration and branch paths intentionally. Buffer-size handling follows xattr probe conventions and can return `-ERANGE`.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
