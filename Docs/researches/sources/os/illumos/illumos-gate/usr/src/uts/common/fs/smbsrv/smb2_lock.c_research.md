# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_lock.c

Read completely. This file implements SMB2 byte-range locking.

`smb2_lock()` decodes the SMB2 lock request, resolves the FID, validates lock count and node presence, applies dialect-specific lock-sequence replay handling, allocates and decodes the `SMB2_LOCK_ELEMENT` array, then dispatches either unlock processing or lock processing based on the first element’s flags. Persistent durable handles trigger `smb2_dh_update_locks()` after successful processing.

`smb2_unlock()` requires every element to be an unlock element and calls `smb_unlock_range()` for each range. `smb2_locks()` processes nonblocking lock arrays, validates flag combinations, maps shared/exclusive flags to internal lock types, rejects mixed invalid forms, and rolls back previously acquired locks if a later element fails.

`smb2_lock_blocking()` handles the special one-element blocking lock case. It first tries a zero-timeout lock to avoid async overhead. If the result means it would block, it sends an indefinite async interim response with `smb2sr_go_async_indefinite()` and then retries with an effectively infinite timeout.

Lock replay support uses SMB2 `LockSequenceIndex` and `LockSequenceNumber`. `smb2_lock_chk_lockseq()` detects repeated successful operations for durable/resilient reconnect scenarios, while `smb2_lock_set_lockseq()` records successful sequences in `ofile->f_lock_seq`. SMB2 ignores lock PIDs and uses PID zero internally.
