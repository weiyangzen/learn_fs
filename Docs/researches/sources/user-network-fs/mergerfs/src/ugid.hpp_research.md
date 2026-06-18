# sources/user-network-fs/mergerfs/src/ugid.hpp

## Purpose
Provides helpers for temporarily switching effective UID/GID while serving FUSE requests.

## Important APIs, Types, and Functions
`ugid_t` stores uid/gid from explicit values or `fuse_req_ctx_t`. `ugid::set()` uses raw `setreuid`/`setregid` syscalls and thread-local current IDs. `ugid::SetGuard` switches on construction and restores on destruction.

## Control Flow
`set()` lazily initializes current effective IDs, returns early when already at requested IDs, switches gid then uid, and updates thread-local cache. `SetGuard` asserts current root IDs, calls `set()`, and restores the previous IDs in its destructor.

## State and Persistence Behavior
State is thread-local process credential tracking plus actual effective credentials. No file persistence occurs.

## Dependencies and Integration Points
Depends on FUSE request context, syscall numbers, `predictability.h`, and POSIX credential APIs. Filesystem operations use it to act as the requesting user.

## Risks and Edge Cases
Syscall return values are ignored, so failed credential switches could leave incorrect assumptions. Assertions may be disabled. The guard assumes privileged/root starting state.

## Test Signals
Run privileged tests for set/restore, invalid UID/GID assertions, per-thread isolation, failure handling, and file ownership effects.
