# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_mutex.c

## Purpose

`kern_mutex.c` implements DragonFlyBSD's compact shared/exclusive mutex primitive. It provides faster, smaller persistent locks than `lockmgr`, supports blocking and asynchronous lock acquisition, exclusive recursion, shared acquisition, spinlock variants, downgrade, try-upgrade, queued wait links, and abortable requests.

## Main Responsibilities

- Acquires exclusive locks synchronously or asynchronously with `_mtx_lock_ex*()`.
- Acquires shared locks synchronously or asynchronously with `_mtx_lock_sh*()`.
- Provides exclusive spinlock and try-spinlock variants.
- Provides nonblocking exclusive/shared try-locks.
- Downgrades exclusive locks to shared and tries shared-to-exclusive upgrade.
- Releases locks and chains queued waiters in priority order.
- Waits for queued link completion with `mtx_wait_link()`.
- Removes or aborts queued lock requests with `mtx_delete_link()` and `mtx_abort_link()`.

## Core Data Model

`mtx_lock` is an atomic integer containing active count, exclusive bit, wanted bits, and `MTX_LINKSPIN`. `mtx_owner` tracks the exclusive owner. Exclusive waiters and shared waiters are held in circular doubly linked lists `mtx_exlink` and `mtx_shlink`, using caller-supplied `mtx_link_t` nodes. Link state records idle, linked-exclusive, linked-shared, acquired, called-back, or aborted status.

Exclusive waiters have priority over shared waiters to avoid shared-side starvation of exclusive acquisitions.

## Acquisition and Wait Behavior

Exclusive lock acquisition first handles unlocked and recursive-exclusive fast paths. On conflict it obtains `MTX_LINKSPIN`, sets `MTX_EXWANTED`, links the request, and either returns `EINPROGRESS` for async links or blocks in `mtx_wait_link()`.

Shared lock acquisition succeeds immediately when the mutex is not exclusive and no exclusive waiter is pending. Otherwise it links on the shared queue under `MTX_LINKSPIN`, sets `MTX_SHWANTED`, and either returns asynchronously or waits.

`mtx_wait_link()` sleeps on the link until the state changes, integrates indefinite-wait diagnostics unless disabled, uses memory fences so post-acquire loads see the releasing CPU's stores, removes still-linked requests after sleep errors, maps aborts to `ENOLCK`, and resets link state to idle.

## Release, Chaining, and Abort

`_mtx_unlock()` handles final and non-final shared/exclusive releases. On final release it grants queued exclusive requests before shared requests. `mtx_chain_link_ex()` transfers the active count to one exclusive waiter, sets `mtx_owner`, and wakes or calls back that waiter. `mtx_chain_link_sh()` grants all queued shared waiters at once, pre-adjusting the active count for the number of shared links.

`mtx_abort_link()` can abort an idle future request or a linked active request. For linked async requests it calls the callback with `ENOLCK`; for synchronous requests it marks aborted and wakes the sleeper. If the lock was already acquired or callback already made, abort is too late and does not revoke the acquisition.
