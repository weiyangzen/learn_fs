# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_hooks.c

## Purpose
Implements a small VFS hook registration and dispatch facility for mount-related lifecycle events.

## Main Interfaces
- `vfs_hooks_init`: initializes the global hook-list mutex.
- `vfs_hooks_attach`: inserts a `struct vfs_hooks` into the global list.
- `vfs_hooks_detach`: removes a registered hooks object or returns `ESRCH`.
- `vfs_hooks_unmount`: dispatches non-error unmount hooks.
- `vfs_hooks_reexport`: dispatches reexport hooks and stops at the first nonzero error.

## State And Control Flow
A global `LIST_HEAD` stores hook providers and is protected by `vfs_hooks_lock`. Two macros generate dispatch functions: one for hooks that return errors and short-circuit, and one for hooks that run all callbacks unconditionally.

## Dependencies And Integration
Uses `struct mount`, mutexes, BSD queue macros, errno values, and VFS hook structures declared elsewhere.

## Risks And Edge Cases
- Hooks are invoked while holding `vfs_hooks_lock`, so callbacks must avoid reentrant operations that would deadlock or block excessively.
- Detach is pointer-based and returns `ESRCH` if the exact hook object is not present.
- Error-dispatch initializes to `EJUSTRETURN`, so callers must understand that "no hook handled it" is distinguishable from success.

## Filesystem Relevance
Moderate. This is generic VFS extension plumbing used around unmount/reexport behavior, not a filesystem implementation itself.
