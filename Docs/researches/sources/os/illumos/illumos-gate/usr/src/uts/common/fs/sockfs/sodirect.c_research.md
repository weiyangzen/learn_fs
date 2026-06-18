# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sodirect.c

## Purpose
Implements sockfs receive-side support for asynchronous direct copyout using `uioa_t`, intended for DMA-assisted copy hardware such as Intel I/OAT.

## Key Elements
`sod_rcv_init` is called at the start of `recvmsg`. It enables `uioa_t` use only for sufficiently large receives, enabled sodirect sockets, global `uioasync` enablement, non-`MSG_PEEK`, non-loopback, no active socket filters, and non-EOF receive state. On success it replaces the caller's `uio_t` with the embedded `sod_uioa`.

`sod_rcv_done` finalizes async copyout with `uioafini`, restores the original `uio_t`, and frees any mblk chains accumulated on the sodirect pending-free list.

`sod_uioa_mblk_init` schedules async copyout for newly enqueued `M_DATA` mblk chains while `UIOA_ENABLED` is set, marks data blocks with `DBLK_UIOA`, and switches to `UIOA_FINI` if the chain no longer fits or scheduling fails. `sod_uioa_so_init` scans already queued socket receive data and the dump area when transitioning into enabled state, scheduling eligible data and splitting mblk chains when async processing must stop.

`sod_uioa_mblk_done` moves already-copied `DBLK_UIOA` chains to the pending-free list, advances their read pointers to write pointers, and flips the uioa state to finalization. `sod_uioa_mblk` removes eligible queued copied data from socket receive queues, completes it, verifies no copied blocks remain queued in debug builds, and returns copied byte count.

`sod_sock_init`, `sod_sock_fini`, and `sod_init` manage per-socket `sodirect_t` allocation from the `sock_sod_cache`.

## Concurrency and Lifetime
Most queue manipulation requires `so_lock`. The async state lives in `so->so_direct` and must not be freed while copied mblk chains remain on `sod_uioafh`. The code relies on `DBLK_UIOA` marking to distinguish data already copied to user buffers from data still requiring normal socket receive processing.

## Edge Cases and Risks
The mblk chain splitting and receive-queue relinking are fragile: incorrect `b_next`, `b_prev`, or `b_cont` updates would corrupt socket receive queues. Async copyout is deliberately disabled for peeks, loopback, filters, EOF, insufficient receive size, out-of-band mark crossings, and overflow of the target uio. The code must preserve the invariant that `DBLK_UIOA` data is not later delivered through normal receive copy paths.
