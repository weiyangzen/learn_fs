# sources/user-network-fs/samba/source4/ntvfs/ipc/vfs_ipc.c

Purpose: implements the default `NTVFS_IPC` backend for IPC$ shares. It accepts tree connects, opens named pipes, bridges SMB read/write/trans/ioctl operations to Samba named-pipe `tstream` transports, and rejects ordinary filesystem operations that do not make sense on IPC$.

Important APIs and types: `struct ipc_private` owns per-share state and the list of open `pipe_state` objects. `pipe_state` binds an `ntvfs_handle` to a lower named pipe stream plus `file_type`, `device_state`, allocation size, and serialized read/write `tevent_queue`s. Key entry points are `ipc_connect`, `ipc_open`, `ipc_read`, `ipc_write`, `ipc_trans`, `ipc_ioctl`, `ipc_close`, `ipc_exit`, `ipc_logoff`, and `ntvfs_ipc_init`.

Control flow: `ipc_connect` normalizes the share path and installs IPC filesystem/device labels. `ipc_open` validates pipe names, creates an NTVFS handle, creates queue state, builds `auth_session_info_transport`, and asynchronously calls `tstream_npa_connect_send`; `ipc_open_done` publishes SMB1/SMB2 open outputs and attaches backend data. Generic read/write/close levels are delegated to `ntvfs_map_*`, while `RAW_*_GENERIC` operations perform queued tstream I/O and reply asynchronously. `ipc_trans` handles `\\PIPE\\LANMAN` RAP, named-pipe handle state, and DCERPC transact write-then-read. SMB2 `FSCTL_NAMED_PIPE_READ_WRITE` follows the same write/read pattern.

State and persistence: pipe state is memory-only and talloc-scoped to handles. The destructor removes it from `pipe_list` and destroys handle backend data. `exit` and `logoff` close matching pipes. No persistent files are created by this backend; durable effects are delegated to named-pipe servers.

Dependencies and integration points: uses NTVFS handle callbacks, tevent async state, `tstream_npa`, named-pipe auth, RAP IPC helpers, tsocket local/remote addresses, and generic NTVFS mappers. `ntvfs_ipc_init` registers backend name `default` for `NTVFS_IPC`.

Risks: async completion must always set status and send exactly once; read/trans/ioctl paths explicitly reject concurrent reads with `NT_STATUS_PIPE_BUSY`; invalid fnum conversion or stale handles produce `INVALID_HANDLE`; pipe-name validation only permits alnum and underscore after lowercasing. Test signals include IPC$ tree connect, SMB1/SMB2 pipe open variants, concurrent transact/read busy behavior, buffer overflow reporting via `STATUS_BUFFER_OVERFLOW`, logoff/exit cleanup, and unsupported filesystem operations returning access-denied style statuses.
