# File Research: sources/os/linux/linux/fs/dlm/plock.c

## Role

`plock.c` bridges kernel POSIX byte-range locks to userspace `dlm_controld` through the `dlm_plock` misc device. It exports the kernel-facing DLM POSIX lock API and implements the device protocol used by userspace to arbitrate locks cluster-wide.

## Operation Queues

`send_list` holds plock operations waiting for userspace to read. `recv_list` holds operations waiting for userspace replies. `ops_lock` protects both lists. `send_wq` wakes the daemon for new requests; `recv_wq` wakes kernel waiters when replies arrive.

`struct plock_op` contains `dlm_plock_info` plus optional async callback data for NFS-style asynchronous lock handling.

## Kernel Lock APIs

`dlm_posix_lock()` sends lock requests. Blocking requests wait for replies and handle signal interruption by sending a cancel. Async requests store a copy of the file lock and return `FILE_LOCK_DEFERRED`.

`dlm_posix_unlock()` first updates the local VFS lock state, then sends an unlock to userspace. Close-generated unlocks do not wait for a reply.

`dlm_posix_cancel()` supports async cancellation, finds the matching waiter, calls the original grant callback with `-EINTR`, or falls back to unlock if cancellation was too late.

`dlm_posix_get()` asks userspace for conflicting lock information and converts positive conflict replies into a VFS `file_lock` result.

## Device Protocol

`dev_read()` returns one `dlm_plock_info` from `send_list`; ordinary requests move to `recv_list`, while close unlocks are freed immediately.

`dev_write()` copies in one result, checks protocol version, matches it to a waiting op, copies the result, and either wakes waiters or invokes the async callback.

`dev_poll()` reports readable state when `send_list` is non-empty.

## Important Behaviors and Invariants

- Blocking waiter replies may arrive out of order, so waiting lock replies match on full lock identity.
- Non-waiting replies are matched to the first non-waiting op for the same filesystem id.
- The filesystem's local VFS lock state is updated after successful cluster lock grant.
- Async callback failure after grant is logged as a dangling-lock risk because cancellation is not fully implemented there.
- Device protocol version mismatch rejects userspace replies.

## Research Notes

Read completely. This file is one of the user/kernel boundary points for DLM and depends on a userspace daemon for cluster-wide POSIX lock arbitration.
