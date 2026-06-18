# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_lock_byte_range.c

This file implements the legacy SMB1 `SMB_COM_LOCK_BYTE_RANGE` command. It is a thin request decoder and protocol wrapper around the core byte-range locking logic in `smb_lock.c`.

Key responsibilities:
- Emits DTrace start/done probes for `op__LockByteRange`.
- Decodes the SMB1 fixed parameter words: FID, byte count, and 32-bit offset.
- Looks up the target open file.
- Applies an exclusive byte-range lock with no wait.
- Encodes an empty SMB result on success.

Important functions:
- `smb_pre_lock_byte_range` and `smb_post_lock_byte_range` provide tracing hooks.
- `smb_com_lock_byte_range` performs decode, file lookup, lock call, error mapping, and response encoding.

Protocol behavior:
- This command only supports 32-bit offsets, so it is unsuitable for general locking in very large files.
- Lock type is always `SMB_LOCK_TYPE_READWRITE`.
- SMB1 lock PID uses the low 16 bits of `sr->smb_pid`.
- Timeout is zero, so conflicts fail immediately.

Dependencies:
- Uses `smbsr_decode_vwv`, `smbsr_lookup_file`, `smb_lock_range`, `smb_lock_range_error`, and `smbsr_encode_empty_result`.

Edge cases:
- Invalid FID returns `NT_STATUS_INVALID_HANDLE` / `ERRbadfid`.
- Any lock failure is delegated to `smb_lock_range_error`.
