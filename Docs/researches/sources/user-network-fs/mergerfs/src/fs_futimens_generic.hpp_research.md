<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_futimens_generic.hpp -->
# sources/user-network-fs/mergerfs/src/fs_futimens_generic.hpp

## Purpose

This header provides a generic `futimens` emulation for platforms without a direct descriptor-based implementation. It validates `timespec` flags, translates `UTIME_NOW`/`UTIME_OMIT`, fetches current timestamps when needed, converts to `timeval`, and calls the project `futimesat` wrapper. The source was read as a complete 281-line file (6101 bytes).

## Important APIs, Types, and Functions

types: `timespec`, `timeval`, `stat` functions: `_can_call_lutimes`, `_should_ignore`, `_should_be_set_to_now`, `_timespec_invalid`, `_flags_invalid`, `_any_timespec_is_utime_omit`, `_any_timespec_is_utime_now`, `_set_utime_omit_to_current_value`, `_set_utime_now_to_now`, `_convert_timespec_to_timeval`, `futimens` macros: `UTIME_NOW`, `UTIME_OMIT`

## Control Flow

Control flow is intentionally thin: validate/translate arguments when needed, call the underlying syscall or project helper, convert errors through negative errno conventions, and return success data or status to higher-level FUSE operations.

## State and Persistence Behavior

The helper does not own long-lived process state. It may mutate kernel filesystem state through descriptors/paths (timestamps, ownership, xattrs, data copy, allocation, sync) and relies on caller-owned descriptors and buffers.

## Dependencies and Integration Points

direct includes: `fs_futimesat.hpp`, `fs_stat_utils.hpp`, `string`, `fcntl.h`, `sys/stat.h`, `sys/time.h`

## Risks and Edge Cases

The main risks are errno polarity mistakes, platform-specific syscall semantics, descriptor/path lifetime bugs, partial copies or timestamp updates, symlink/race behavior, and metadata divergence across backing filesystems.

## Test Signals

Filesystem integration tests on temporary directories/files covering success, ENOENT/EACCES/EINVAL paths, symlink behavior, metadata preservation, partial-copy/error injection, and platform-specific fallbacks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_futimens_generic.hpp -->
