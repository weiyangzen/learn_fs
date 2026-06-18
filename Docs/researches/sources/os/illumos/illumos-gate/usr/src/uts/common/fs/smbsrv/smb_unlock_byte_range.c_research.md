# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_unlock_byte_range.c

Implements legacy SMB1 `SMB_COM_UNLOCK_BYTE_RANGE`. The command unlocks a 32-bit byte range previously locked on a file handle.

The handler decodes FID, length, and offset from the parameter words, looks up the open file, rejects invalid handles, derives the SMB1 16-bit lock PID from `sr->smb_pid`, and calls `smb_unlock_range` with 64-bit offset and length conversions. If unlock fails, it reports `NT_STATUS_RANGE_NOT_LOCKED` / `ERROR_NOT_LOCKED`; otherwise it returns an empty SMB result.

The file also provides pre/post DTrace probe wrappers. The comments document SMB semantics that unlocking a range not locked should generate no protocol error, though this implementation maps non-success from `smb_unlock_range` to range-not-locked.
