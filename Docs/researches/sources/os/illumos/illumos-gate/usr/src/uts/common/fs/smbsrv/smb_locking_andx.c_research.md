# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_locking_andx.c

This file implements SMB1 `SMB_COM_LOCKING_ANDX`, which can acknowledge oplock breaks, cancel pending locks, unlock ranges, and lock ranges in one request.

Key responsibilities:
- Emits DTrace start/done probes for `op__LockingX`.
- Decodes lock type, oplock level, timeout, unlock count, and lock count.
- Validates target file and element counts.
- Handles oplock release acknowledgements.
- Rejects atomic lock-type conversion as unsupported.
- Supports normal and large-file lock element formats.
- Performs unlocks first, then locks.
- Rolls back already granted locks if a later lock in the same request fails.
- Encodes the AndX response.

Important functions:
- `smb_com_locking_andx` is the command implementation.
- Local `struct lreq` normalizes 32-bit and 64-bit lock/unlock elements into offset, length, and 16-bit PID.

Protocol behavior:
- `LOCKING_ANDX_SHARED_LOCK` maps to `SMB_LOCK_TYPE_READONLY`; absence maps to exclusive/read-write lock.
- `LOCKING_ANDX_OPLOCK_RELEASE` calls `smb1_oplock_ack_break`; if no lock/unlock elements are present, no reply is sent.
- `LOCKING_ANDX_CHANGE_LOCK_TYPE` returns `ERROR_ATOMIC_LOCKS_NOT_SUPPORTED`.
- `LOCKING_ANDX_LARGE_FILES` requires dialect `NT_LM_0_12` or later.
- `LOCKING_ANDX_CANCEL_LOCK` cancels one matching pending lock using the first lock vector entry.

Dependencies:
- Lock operations are delegated to `smb_unlock_range`, `smb_lock_range`, and `smb_lock_range_cancel`.
- Element parsing uses `smb_mbc_decodef`.
- Response uses `smbsr_encode_result`.

Edge cases and protections:
- `smb_lock_max_elem` limits each vector to 1024 elements to bound allocation.
- Decode failure returns the Windows-compatible `ERRSRV/ERRerror`.
- Failed unlock returns `NT_STATUS_RANGE_NOT_LOCKED` / `ERROR_NOT_LOCKED`.
- Failed lock rolls back locks already acquired in the same request.
