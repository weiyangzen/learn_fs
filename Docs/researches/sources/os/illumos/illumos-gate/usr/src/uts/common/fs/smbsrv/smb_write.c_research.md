# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_write.c

## Purpose
Implements SMB1 server write command handling for normal writes, write-and-close, write-and-unlock, obsolete write-raw rejection, WriteAndX, and the common write/truncate backend.

## Main Behavior
- Each SMB command has pre/post handlers that allocate/free `smb_rw_param_t`, decode request words/data offsets, and emit DTrace start/done probes.
- `smb_com_write()` writes at a 32-bit offset; a zero byte count truncates or extends the disk file to the offset.
- `smb_com_write_and_close()` performs the same write/truncate operation, then closes the open file with an optional last-write timestamp.
- `smb_com_write_and_unlock()` only allows disk tree shares, writes the data, then unlocks the written range using the SMB1 16-bit PID.
- `smb_com_write_raw()` is retained only for observability and always returns `NT_STATUS_NOT_SUPPORTED`.
- `smb_pre_write_andx()` supports 12-word and 14-word forms, including 64-bit offsets and large writes via `CAP_LARGE_WRITEX` or a Win7 compatibility heuristic.
- `smb_common_write()` dispatches by share type: disk/print queues go through filesystem write paths and byte-range lock checks; IPC writes go through named pipe write handling.
- `smb_write_truncate()` applies `SMB_AT_SIZE` via `smb_node_setattr()` after checking range lock access.

## Integration Points
- Depends on SMB request decode/encode helpers, `smbsr_lookup_file()`, ofile credentials, byte-range lock helpers, SMB filesystem operations, named pipe writes, oplock breaking, and node notification.
- Uses `smb_ofile_t` seek position updates after successful write/truncate.
- Updates change-notification behavior lazily through `f_written` and `smb_node_notify_modified()` rather than notifying every write.

## Risks and Notes
- `smb_com_write_and_close()` contains an explicit comment questioning whether its data decode format should be `"3.#B"` instead of `".#B"`.
- Partial write counts are reflected back to clients; most successful filesystem writes are expected to match the requested count.
- Stable-write mode and node write-through flags map to `FSYNC`.
- Lock-conflict paths set SMB errors directly and suppress generic errno translation.
