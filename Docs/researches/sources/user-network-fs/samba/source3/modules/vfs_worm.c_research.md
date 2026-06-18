# sources/user-network-fs/samba/source3/modules/vfs_worm.c

## Purpose
`vfs_worm.c` implements write-once-read-many behavior by denying write or metadata-changing operations on files older than a configured grace period. It protects both file data and ACL/xattr/attribute mutation once the ctime age crosses the threshold.

## Important APIs, Types, and Functions
`struct worm_config_data` stores `grace_period`. `write_access_flags` combines data, append, attribute, delete, owner, DACL, and EA write bits. `vfs_worm_connect()` reads `worm:grace_period` except for IPC/print shares. `is_readonly()` and `fsp_is_readonly()` compare stat ctime age with the grace period. The module hooks `create_file`, `openat`, `fntimes`, `fchmod`, `fchown`, `renameat`, `fsetxattr`, `fremovexattr`, `unlinkat`, DOS attributes, NT ACLs, POSIX ACL set/delete, and rejects changes when readonly.

## Control Flow
On create/open, readonly files with requested or granted write access are denied. Metadata and ACL/xattr operations check readonly before calling the next VFS method. Rename denies if the source is protected and also checks an existing destination path to prevent overwriting a protected target. Unlink builds a full filename, checks readonly, then delegates.

## State and Persistence
The module stores only per-share grace-period config. Protection state is inferred from filesystem ctime, not stored separately. No persistent marker is written by this module.

## Dependencies and Integration Points
It depends on Samba security access masks, stat timestamps, VFS full-path helpers, and next-module operations. It registers as `worm` and is built as an optional VFS module.

## Risks
Using ctime means administrative metadata changes can reset or affect protection timing depending on filesystem semantics. Operations with invalid stat default to readonly in handle-data failure cases but not when stat is simply invalid inside helper flow. Rename destination protection was explicitly added for a CVE fix, so overwrite and race behavior around destination lookup is high risk.

## Test Signals
Tests should cover files younger/older than grace period, MAXIMUM_ALLOWED access, write and metadata operations, unlink of protected files, rename source and destination protection, xattr/ACL denial, IPC/print share bypass, and ctime boundary conditions.
