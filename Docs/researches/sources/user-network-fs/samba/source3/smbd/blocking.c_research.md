# sources/user-network-fs/samba/source3/smbd/blocking.c

## Purpose
`blocking.c` implements SMB1 blocking byte-range lock handling. It tries multi-lock requests atomically, queues requests that cannot complete immediately, waits on share-mode/locking database notifications or retry timers, and exposes cancellation helpers used by legacy SMB1 lock/cancel paths.

## Important APIs, types, and functions
- `smbd_do_locks_try()` loops over `struct smbd_lock_element` entries, calls `do_lock()`, records the blocker, and unwinds already acquired locks with `do_unlock()` if any later lock fails.
- `smbd_smb1_do_locks_send()` creates a `tevent_req` for a lock request, moves the `smb_request` into request state, performs the first try, and appends in-progress requests to `fsp->blocked_smb1_lock_reqs`.
- `smbd_smb1_do_locks_try_fn()` is the locked share-mode callback. It checks older blocked requests for fairness, calls `smbd_do_locks_try()`, and sets up `share_mode_watch_send()` plus timeout/backoff behavior.
- `smbd_smb1_do_locks_recv()` returns the final status and records repeated lock failure offset hints on the FSP.
- `smbd_smb1_brl_finish_by_req()`, `smbd_smb1_brl_finish_by_lock()`, and `smbd_smb1_brl_finish_by_mid()` complete blocked requests by direct request, matching lock tuple, or SMB1 MID.

## Control flow
A lock request enters `smbd_smb1_do_locks_send()`. Empty lock batches complete immediately. Otherwise the request tries to acquire locks under `share_mode_do_locked_brl()`. The callback first checks older requests in the same FSP blocked-list so a younger request cannot bypass a conflicting older one. If the byte-range lock backend grants all locks, the request completes. If it returns `NT_STATUS_RETRY`, Samba waits either for locking database wakeups or a retry timer, ignoring the client timeout until the backend gives a definitive result. If it returns a lock-denied status, Samba computes an end time from client timeout, `lp_lock_spin_time()`, ancient large-offset heuristics, and prior failure offset state. POSIX lock conflicts use polling because the backend identifies them with `blocking_smblctx == UINT64_MAX`.

## State and persistence behavior
The persistent lock state lives in Samba locking/share-mode databases via the byte-range locking layer, not in this file. This file owns transient tevent state and the per-FSP `blocked_smb1_lock_reqs` array. Request cleanup removes entries from that array unless the request was already received. `fsp->fsp_flags.lock_failure_seen` and `fsp->lock_failure_offset` store a short-lived hint to delay repeated lock attempts on the same offset.

## Dependencies and integration points
The file depends on byte-range locking (`do_lock`, `do_unlock`, `brl_*`), share-mode locking/watch APIs, messaging server IDs, tevent, request lifetime management, and SMB1 cancel/lock reply code. It integrates with `close.c`, which drains blocked lock requests before closing a normal file.

## Risks and edge cases
- `smbd_smb1_do_locks_check_blocked()` indexes `blocked[li]` inside the `bi` loop; this deserves review because it appears intended to inspect `blocked[bi]`.
- Incorrect cleanup of `fsp->blocked_smb1_lock_reqs` can leave waiters on dead FSPs or complete the wrong SMB1 request.
- Backend `NT_STATUS_RETRY` can wait indefinitely by design; backends must eventually return another status.
- POSIX lock polling and share-mode wakeups can retry on unrelated database changes.
- Cancellation by MID walks all FSPs and is intentionally expensive but legacy-only.

## Test signals
Useful tests cover multi-lock atomic rollback, lock denial versus timeout status mapping, FIFO behavior among blocked SMB1 locks, MID cancellation, matching lock cancellation, POSIX lock polling, and close-time draining of blocked locks with `NT_STATUS_RANGE_NOT_LOCKED`.
