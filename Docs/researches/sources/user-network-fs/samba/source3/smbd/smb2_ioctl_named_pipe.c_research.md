# sources/user-network-fs/samba/source3/smbd/smb2_ioctl_named_pipe.c

Purpose: handles named-pipe FSCTLs, primarily `FSCTL_PIPE_TRANSCEIVE`, using async pipe write/read operations.

Important APIs: `smb2_ioctl_named_pipe()` dispatches controls. `smbd_smb2_ioctl_pipe_write_done()` receives `np_write_send()`. `smbd_smb2_ioctl_pipe_read_done()` receives `np_read_send()` and signals overflow when more pipe data remains.

Control flow: transceive requires IPC, a valid fsp, and `fsp_is_np()`. It writes the input buffer to the pipe fake file handle, maps pipe transport errors through `nt_status_np_pipe()`, requires a full write, allocates an output buffer of `in_max_output`, and reads the reply. The read callback maps errors, shrinks output length to bytes read, returns `STATUS_BUFFER_OVERFLOW` if data remains, or completes. Other named-pipe controls use `SMB_VFS_FSCTL()` and unsupported-status mapping.

State and persistence: per-request shared IOCTL state plus external named-pipe server state. Output is talloc-owned by the IOCTL state.

Dependencies and integration: depends on IPC checks, pipe fake file handles, `np_write`/`np_read`, pipe status mapping from `smb2_ipc.c`, VFS FSCTL fallback, and the IOCTL front door's allowed overflow handling.

Risks: partial writes return `PIPE_NOT_AVAILABLE`. `STATUS_BUFFER_OVERFLOW` must remain a data-bearing IOCTL response. Async pipe operations must survive handle close through front-door AIO registration. Non-IPC status mapping must distinguish unsupported from invalid device.

Test signals: cover transceive on non-IPC, null/closed/non-pipe fsp, pipe disconnect/reset, partial output overflow, zero max output, and close while transceive is pending.
