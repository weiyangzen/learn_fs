# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-utils.c

## Scope

This file provides OrangeFS kernel utility glue for mapping VFS inode state to OrangeFS protocol attributes, refreshing inode attributes through userspace client upcalls, detecting stale cached inodes, writing dirty inode attributes back, extracting fsids from operation unions, translating OrangeFS protocol errors to Linux errno values, and converting Linux mode bits to OrangeFS permission bits.

## Public And Internal APIs Covered

- `fsid_of_op()` extracts the filesystem id from operation-specific upcall payloads.
- Attribute translators: `orangefs_inode_flags()`, `orangefs_inode_perms()`, `copy_attributes_from_inode()`, `orangefs_inode_type()`.
- Inode validity helpers: `orangefs_make_bad_inode()` and `orangefs_inode_is_stale()`.
- Attribute operations: `orangefs_inode_getattr()`, `orangefs_inode_check_changed()`, `orangefs_inode_setattr()`.
- Error and mode conversion: `orangefs_normalize_to_errno()` and `ORANGEFS_util_translate_mode()`.

## Control Flow And Behavior

- `orangefs_inode_getattr()` first checks OrangeFS attribute cache timeout, pending local attribute updates, and dirty page state under `inode->i_lock`. If local setattr state is pending, it forces `write_inode_now()` and retries before issuing a remote GETATTR.
- GETATTR requests ask for all low-cost attributes and only include size when the caller passes flags. New inodes can accept symlink target initialization; existing inodes validate type and symlink target to detect stale objects.
- Regular file refresh updates immutable/append/noatime flags, size, block size, byte count, and block count. Directory refresh reports `PAGE_SIZE` size and nlink 1. Symlink refresh stores the target in OrangeFS private inode storage and points `inode->i_link` at it.
- `orangefs_inode_setattr()` snapshots delayed VFS changes from `orangefs_inode->attr_valid`, converts uid/gid/mode/time masks to `ORANGEFS_sys_attr_s`, clears pending state, and sends a writeback SETATTR upcall. Failure marks the inode bad except for root.
- `orangefs_inode_check_changed()` performs a narrow GETATTR for object type and link target to test whether a cached inode is still valid.
- `orangefs_normalize_to_errno()` handles success, positive server errors, OrangeFS non-errno protocol errors such as cancel, and encoded errno values via `PINT_errno_mapping`.

## State And Data Structures

- Uses `struct orangefs_inode_s` fields including `refn`, `attr_valid`, `attr_uid`, `attr_gid`, `getattr_time`, and `link_target`.
- Uses protocol structures `struct ORANGEFS_sys_attr_s`, `struct orangefs_kernel_op_s`, and `struct orangefs_object_kref`.
- Local inode state touched includes `i_flags`, `i_mode`, `i_uid`, `i_gid`, timestamps, size, block accounting, and symlink `i_link`.

## Dependencies

- Depends on OrangeFS operation allocation/service helpers: `op_alloc()`, `service_operation()`, and `op_release()`.
- Uses OrangeFS protocol constants from `protocol.h` and operation type definitions from OrangeFS kernel headers.
- Relies on VFS helpers for inode writeback, bad inode marking, dirty-page state, uid/gid conversion, and timestamp accessors.

## Risks And Invariants

- Attribute cache checks must be serialized with local pending setattr state; otherwise stale remote attributes could overwrite local changes.
- Root inode is deliberately not converted to a bad inode after userspace client loss because losing root inode operations would destabilize the mount.
- Symlink target comparison is part of stale detection; changed remote link targets invalidate cached symlink inodes.
- Error normalization is a protocol boundary. Unknown or malformed OrangeFS errors are mapped to `-EINVAL` after logging.
