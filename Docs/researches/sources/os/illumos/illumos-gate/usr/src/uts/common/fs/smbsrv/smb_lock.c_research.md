# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_lock.c

This file implements SMB byte-range locking. It maintains granted and waiting lock lists on `smb_node_t`, enforces SMB lock compatibility rules, mirrors locks into filesystem/POSIX record locks, handles blocking waits and cancellation, and translates vnode/NBL conflicts to SMB status codes.

Key responsibilities:
- Counts locks held by an open file.
- Grants and releases SMB byte-range locks.
- Checks read/write access against existing SMB range locks.
- Cancels waiting locks.
- Destroys all locks associated with an ofile on close.
- Mirrors successful locks/unlocks through `smb_fsop_frlock`.
- Handles waiting lock wakeup ordering.
- Checks share/byte-range conflicts through illumos NBML interfaces.

Important functions:
- `smb_lock_range` creates a desired lock, applies lock rules, waits if allowed, mirrors to the filesystem, inserts into `node->n_lock_list`, and breaks read-cache delegations on success.
- `smb_unlock_range` finds an exact lock match, removes it, unlocks POSIX-visible ranges not still covered by same-ofile locks, and destroys the SMB lock.
- `smb_lock_range_access` denies reads/writes that conflict with SMB locks from other file/PID contexts.
- `smb_node_destroy_lock_by_ofile` cancels waiters and moves matching granted locks to a temporary list before destroying them.
- `smb_lock_range_cancel` marks a matching waiting lock cancelled.
- `smb_nbl_conflict` maps NBL share and lock conflicts to SMB status values.
- `smb_lock_wait` records dependency on a conflicting lock, moves request state to `SMB_REQ_STATE_WAITING_LOCK`, waits with timeout/cancel support, and restores state.
- `smb_lock_destroy` wakes waiting locks blocked by the destroyed lock.
- `smb_is_range_unlocked` determines subranges that can be released from POSIX locks without releasing overlapping SMB locks.

Lock semantics:
- Exact unlock match requires same start, length, ofile, and PID.
- Read-only locks can overlap other read-only locks.
- A read-only lock may overlap a write lock held by the same file and PID.
- Write locks conflict with overlapping locks unless compatible by the above rules.
- Zero-length ranges have special overlap semantics: they affect no bytes but can conflict with positive-length ranges containing their offset.
- SMB1 compatibility affects error mapping for some lock failures.

Concurrency and lifetime:
- Granted locks live on `node->n_lock_list`; waiting locks live on `node->n_wlock_list`.
- List locks are held through `smb_llist_enter/exit`.
- `smb_lock_wait` deliberately drops `n_lock_list` while sleeping and reacquires it before returning.
- Waiting locks use `l_mutex`, `l_cv`, `l_blocked_by`, `l_flags`, and `l_conflicts`.
- Close/cancel paths broadcast on waiting lock CVs.
- Destruction wakes waiters one at a time with a small delay to preserve FIFO-ish behavior.

Filesystem relevance:
- Locks are mirrored into filesystem byte-range locks through `smb_fsop_frlock`.
- `smb_lock_posix_unlock` avoids dropping POSIX locks for ranges still covered by other SMB locks on the same ofile.
- `smb_nbl_conflict` participates in remove/rename/read/write conflict checks against vnode NBML state.

Edge cases and risks:
- Range overflow is rejected when `start + length` wraps.
- `NT_STATUS_FILE_CLOSED` is translated to `NT_STATUS_RANGE_NOT_LOCKED` in some lock failure paths.
- The code carefully avoids lock-order inversion with vnode `vnbllock` by not walking ofiles inside `smb_nbl_conflict`.
- Unlock POSIX subrange logic depends on lock list consistency while caller holds `n_lock_list`.
