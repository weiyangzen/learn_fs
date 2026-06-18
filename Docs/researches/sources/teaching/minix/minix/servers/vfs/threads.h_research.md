# File Research: sources/teaching/minix/minix/servers/vfs/threads.h

## Purpose
Adapts MINIX `mthread` primitives to VFS-local thread, mutex, condition, and attribute names, and defines the per-worker state structure.

## Main Types and Macros
- Aliases `thread_t`, `mutex_t`, `cond_t`, `attr_t` to `mthread_*` types.
- Aliases mutex and condition operations to `mthread_*` functions.
- Defines `struct worker_thread`.

## Worker State
`struct worker_thread` stores:
- thread identity and event synchronization objects,
- current process context `w_fp`,
- input/output messages and saved error code,
- blocked sendrec storage for FS and driver communication,
- current task endpoint and device map pointer,
- `w_next` queue linkage used by the TLL locking queues.

## Dependencies
Includes `<minix/mthread.h>` and forward-declares `struct fproc`.

## Risks and Notes
`w_next` is shared by worker scheduling and TLL wait queues, so lock code assumes a worker is on at most one such queue at a time.
