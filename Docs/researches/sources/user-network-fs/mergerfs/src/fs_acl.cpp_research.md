<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_acl.cpp -->
# sources/user-network-fs/mergerfs/src/fs_acl.cpp

## Purpose

This implementation provides the mergerfs filesystem helper for ACL default-detection helper for directories, based on `system.posix_acl_default` xattrs. It integrates lower-level syscalls with mergerfs copy/search/metadata logic. The source was read as a complete 40-line file (1195 bytes).

## Important APIs, Types, and Functions

functions: `fs::acl::dir_has_defaults`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_acl.hpp`, `fs_lgetxattr.hpp`, `fs_path.hpp`, `filesystem`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_acl.cpp -->
