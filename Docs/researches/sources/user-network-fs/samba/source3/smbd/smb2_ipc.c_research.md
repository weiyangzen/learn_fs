# sources/user-network-fs/samba/source3/smbd/smb2_ipc.c

Purpose: provides named-pipe status normalization for SMB2 IPC paths.

Important API: `nt_status_np_pipe()` maps `NT_STATUS_CONNECTION_DISCONNECTED` to `NT_STATUS_PIPE_DISCONNECTED` and `NT_STATUS_CONNECTION_RESET` to `NT_STATUS_PIPE_BROKEN`; other statuses pass through unchanged.

Control flow: the helper is called after named-pipe read/write operations so clients receive pipe-domain errors rather than lower-level connection statuses.

State and persistence: no state or persistence.

Dependencies and integration: depends on Samba `NTSTATUS` helpers and integrates with `smb2_ioctl_named_pipe.c` pipe transceive callbacks and other IPC code needing Windows-compatible pipe errors.

Risks: the mapping is deliberately narrow. Adding or removing mappings changes RPC/named-pipe client retry and disconnect behavior.

Test signals: pipe disconnect/reset tests should observe `PIPE_DISCONNECTED` or `PIPE_BROKEN` rather than generic connection statuses.
