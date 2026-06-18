<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copyfile.cpp -->
# sources/user-network-fs/mergerfs/src/fs_copyfile.cpp

## Purpose

This implementation provides the mergerfs filesystem helper for high-level copy helper that creates a temporary destination, copies data, restores owner/mode/timestamps/attrs, checks source stability, and optionally cleans up on failure. It integrates lower-level syscalls with mergerfs copy/search/metadata logic. The source was read as a complete 185-line file (4733 bytes).

## Important APIs, Types, and Functions

types: `stat`, `sigaction` functions: `fs::copyfile`, `_ignorable_error`, `std::tie`, `fs::fcntl_setlease_rdlck`, `fs::unlink` macros: `O_NOATIME`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_copyfile.hpp`, `fs_attr.hpp`, `fs_close.hpp`, `fs_copydata.hpp`, `fs_fchmod.hpp`, `fs_fchown.hpp`, `fs_fcntl.hpp`, `fs_file_unchanged.hpp`, `fs_fstat.hpp`, `fs_futimens.hpp`, `fs_mktemp.hpp`, `fs_open.hpp`, `fs_path.hpp`, `fs_rename.hpp`, and 5 more

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_copyfile.cpp -->
