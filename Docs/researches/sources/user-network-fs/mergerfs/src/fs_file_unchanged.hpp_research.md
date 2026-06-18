<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_file_unchanged.hpp -->
# sources/user-network-fs/mergerfs/src/fs_file_unchanged.hpp

## Purpose

This header declares or defines the mergerfs filesystem helper for post-copy source stability checker comparing stat metadata. It is part of the project wrapper layer that normalizes POSIX/syscall behavior into negative errno returns and `fs::path` types. The source was read as a complete 54-line file (1557 bytes).

## Important APIs, Types, and Functions

types: `stat` functions: `file_changed` macros: `FS_FILE_CHANGED`, `FS_FILE_UNCHANGED`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_fstat.hpp`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_file_unchanged.hpp -->
