# sources/user-network-fs/samba/source4/ntvfs/ntvfs_generic.c

Purpose: maps legacy SMB1 and SMB2 operation variants onto a smaller set of generic backend calls, then maps generic results back to the caller's requested information level. It lets backends implement canonical operations while preserving protocol-specific behavior.

Important APIs and functions: async support is implemented by `struct ntvfs_map_async`, `ntvfs_map_async_setup`, `ntvfs_map_async_finish`, and `ntvfs_map_async_send`. Public mappers include `ntvfs_map_open`, `ntvfs_map_fsinfo`, `ntvfs_map_fileinfo`, `ntvfs_map_qfileinfo`, `ntvfs_map_qpathinfo`, `ntvfs_map_lock`, `ntvfs_map_write`, `ntvfs_map_read`, `ntvfs_map_close`, and `ntvfs_map_notify`. `map_openx_open` translates OpenX access/share/disposition rules and `is_exe_filename` implements DOS deny-mode quirks.

Control flow: each mapper allocates a second union, pushes an async state containing original/new I/O and a finish callback, calls the backend's generic operation, then either returns pending async status or immediately pops the state and maps outputs. Open mapping handles Open/OpenX/T2Open/MkNew/Create/CTemp/SMB2; write/read mapping handles older write/read forms and SMB2; close and notify convert SMB2 outputs; file/fs info mapping fan out generic metadata into many raw levels.

State and persistence: only per-request talloc state is created. Some mappers issue synchronous secondary calls, such as setting write time or size after create, unlocking after write-unlock, locking before lock-read, or closing after write-close.

Dependencies and integration points: dispatches through `ntvfs->ops` and async-state helpers. It encodes SMB constants, NT create options, security masks, oplock level mapping, and info-level unions from raw protocol headers.

Risks: compatibility behavior is subtle, especially deny modes, SMB2 unsupported create options, `MAXIMUM_ALLOWED`, Unix info levels intentionally invalid, buffer allocations for streams/EAs, and secondary calls with async disabled. Test signals should cover every raw level, async and immediate backend completion, SMB2 create option rejection, OpenX created-size extension, lock flag validation, and notify empty-change mapping to `NT_STATUS_NOTIFY_ENUM_DIR`.
