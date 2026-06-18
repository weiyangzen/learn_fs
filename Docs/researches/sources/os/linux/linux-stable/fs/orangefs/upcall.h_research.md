# File Research: sources/os/linux/linux-stable/fs/orangefs/upcall.h

## Scope

This header defines the fixed-layout request side of the OrangeFS kernel-to-userspace upcall protocol. It contains one structure per VFS operation class plus the top-level `struct orangefs_upcall_s` union sent to client-core.

## APIs And Structures

- File I/O: `struct orangefs_io_request_s` with shared-buffer index, count, offset, object ref, I/O type, and readahead size.
- Namespace operations: lookup, create, symlink, remove, mkdir, rename.
- Metadata operations: getattr, setattr, truncate, fsync, statfs.
- Directory iteration: readdir and readdirplus with tokens, count, masks, and buffer index.
- Mount lifecycle: fs mount, fs unmount, fs key, and feature negotiation requests.
- Xattrs: getxattr, setxattr, listxattr, removexattr.
- Control and tuning: cancel, parameter get/set operations, performance counter requests.
- Top-level `struct orangefs_upcall_s` includes operation type, uid/gid, pid/tgid, compatibility trailer fields, and a union of request payloads.

## Control Flow And Behavior

- Kernel callers allocate `struct orangefs_kernel_op_s`, populate the appropriate member of `upcall.req`, and submit it through `service_operation()`.
- `uid`, `gid`, `pid`, and `tgid` are filled around service submission to let userspace see the credential/process context.
- Cancel operations reuse an operation object by replacing the upcall with `ORANGEFS_VFS_OP_CANCEL` and the original operation tag.
- Parameter operations cover attribute/name/capability cache limits, performance sampling, debug masks, and readahead settings.

## State And Data Structures

- Many structures include explicit padding fields to preserve 32/64-bit ABI layout.
- Name-bearing requests use fixed `ORANGEFS_NAME_MAX` or `ORANGEFS_MAX_XATTR_NAMELEN` arrays.
- `orangefs_setxattr_request_s` embeds `struct ORANGEFS_keyval_pair`, so xattr values are carried inline up to OrangeFS protocol limits.
- `orangefs_param_request_s` supports 64-bit numeric values, two 32-bit values, or a debug string.

## Dependencies

- Depends on types and constants from `protocol.h`, including object refs, system attributes, I/O types, xattr sizes, and debug string length.

## Risks And Invariants

- The header explicitly preserves protocol compatibility with older userspace; padding and unused trailer fields are part of the ABI.
- Fixed-size arrays bound every request payload; callers must validate names and values before copying into the upcall.
- Changes to enum values or structure layout must be coordinated with client-core.
