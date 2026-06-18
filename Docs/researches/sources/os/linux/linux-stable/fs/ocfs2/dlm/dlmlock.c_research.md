# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmlock.c

## Purpose

`dlmlock.c` implements OCFS2 DLM lock creation and the exported `dlmlock()` API. It handles new lock requests, conversion routing, local master grants, remote create-lock messaging, lock allocation, lock lifetime, cookie generation, and the create-lock network handler.

## Lock Allocation And Lifetime

The file owns the `o2dlm_lock` slab cache:

- `dlm_init_lock_cache()`
- `dlm_destroy_lock_cache()`

Lock objects are kref-managed:

- `dlm_lock_get()`
- `dlm_lock_put()`
- `dlm_lock_release()`

A lock release asserts the lock is on no queue and has no pending AST/BAST state before detaching its lock resource and freeing the lock and optional kernel-allocated LKSB.

`dlm_new_lock()` allocates a lock, optionally allocates a kernel LKSB, initializes list heads, spinlock, modes, cookie, pending flags, callbacks, kref, and stores the lock pointer in `lksb->lockid`.

## Cookie Generation

`dlm_get_next_cookie()` creates a u64 cookie by storing the node number in the top 8 bits and a node-local sequence in the lower 56 bits. It wraps when the sequence would enter the top byte.

## Local Master Locking

`dlmlock_master()` is used when the local node owns the lock resource. It waits for the resource to be usable, reserves an AST, then either:

- Grants immediately and queues the lock on `res->granted`.
- Returns `DLM_NOTQUEUED` for incompatible `LKM_NOQUEUE`.
- Queues the lock on `res->blocked` for normal waiting.

`dlm_can_grant_new_lock()` checks compatibility with both granted locks and converting locks, including conversion target modes.

The recovery lock is a special case: if granted, no AST is queued because the DLM thread is frozen during recovery.

## Remote Locking

`dlmlock_remote()` is used when another node owns the lock resource. It waits out resource state changes, marks the resource `DLM_LOCK_RES_IN_PROGRESS`, queues the local lock on the blocked queue, sets `lock_pending`, and sends `DLM_CREATE_LOCK_MSG`.

On success, the remote master has accepted or granted the request. For the `$RECOVERY` lock, the local node manually moves the lock to granted because no AST will arrive.

On failure, the pending local lock is removed from the queue and its reference is dropped. Recovery and migration statuses are routed back to the caller for retry.

## Create Lock Message

`dlm_send_remote_lock_request()` sends `DLM_CREATE_LOCK_MSG` to `res->owner` and converts transport errors into DLM statuses. Host-down style errors become `DLM_RECOVERING`.

`dlm_create_lock_handler()` runs on the master node. It validates:

- DLM context availability.
- Fully joined domain state.
- Name length.
- Lock allocation.
- Lock resource lookup.
- Lock resource state.

It creates a lock for the remote node, applies `DLM_LKSB_GET_LVB` if requested, attaches the lock resource, and calls `dlmlock_master()`.

## Exported API: dlmlock()

`dlmlock()` supports two broad paths:

- New lock request.
- Convert request via `LKM_CONVERT`.

It validates LKSB presence, mode, flags, recovery-lock rules, local-convert rules, and name length.

For conversion:

- The existing lock comes from `lksb->lockid`.
- The existing lock resource is reused.
- Callback and LKSB arguments must match the original lock.
- The request routes to `dlmconvert_master()` or `dlmconvert_remote()`.
- `DLM_RECOVERING`, `DLM_MIGRATING`, and `DLM_FORWARD` cause retry after a short sleep.

For new locks:

- A new cookie and lock are allocated.
- The caller waits for recovery unless this is a recovery-lock request.
- `dlm_get_lock_resource()` finds or masters the lock resource.
- LVB fetch intent is set for eligible lock modes.
- The request routes to local or remote lock handling.
- Inflight references from `dlm_get_lock_resource()` are dropped after the request.

## Concurrency And Invariants

Important invariants:

- New locks acquire and later drop an inflight lock-resource reference.
- Local master grants reserve an AST and must either queue it or release it.
- Remote lock requests use `lock_pending` and `DLM_LOCK_RES_IN_PROGRESS` to serialize state.
- Failed new lock requests drop the newly allocated lock unless this is a convert path.
- Failed lock requests set `lksb->status`.

## Dependencies

This file depends on:

- Conversion APIs from `dlmconvert.h`.
- Lock resource creation/mastering from `dlmmaster.c`.
- AST queueing and DLM thread behavior from the broader DLM.
- Network transport through `o2net_send_message()`.
