# sources/user-network-fs/samba/source3/modules/vfs_delay_inject.c

## Purpose
`vfs_delay_inject.c` injects configurable delays into selected VFS calls for race, timeout, async sequencing, and byte-range-lock testing.

## Important APIs, Types, And Functions
`inject_delay()` reads `delay_inject:<function>` in milliseconds. Async read/write wrappers use `vfs_delay_inject_pread_state` and `vfs_delay_inject_pwrite_state`, optionally inserting `tevent_wakeup_send()` before delegating. Byte-range locks use `vfs_delay_inject_brl_lock_state`, a global DLIST, request GUID matching, optional timers, and share-mode waiter wakeups.

## Control Flow
`fntimes` sleeps synchronously. Async pread/pwrite either delegate immediately or wait for a timer, then call the next async hook and relay the lower result. `brl_lock_windows` allocates state on first request, returns `NT_STATUS_RETRY` until the configured delay expires, then delegates to the next lock hook.

## State And Persistence
Async state is per request. Byte-range lock delay state is process memory linked in `brl_lock_states` and removed by destructor or completion. Configuration is read per operation; nothing is persisted.

## Dependencies And Integration Points
The module depends on tevent, global event context, Samba byte-range lock APIs, share-mode wakeups, and VFS async I/O hooks.

## Risks
Synchronous sleeps block the worker. Global lock-delay state must match request lifetime. Large or negative delays are not locally validated. Timer failure maps to `EIO`. Lock retry semantics depend on `smblctx` values consumed by upper layers.

## Test Signals
Verify zero and nonzero delays, async pread/pwrite timing and callback propagation, wakeup failures, byte-range lock retry with timer and non-timer modes, waiter wakeup, cancellation cleanup, and config isolation by function name.
