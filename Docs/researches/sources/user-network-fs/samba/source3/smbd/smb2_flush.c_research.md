# sources/user-network-fs/samba/source3/smbd/smb2_flush.c

Purpose: implements SMB2 FLUSH for an open file or directory handle. It validates the handle, checks access, optionally issues an asynchronous VFS fsync, and returns the minimal flush response.

Important APIs and types: `smbd_smb2_request_process_flush()` decodes file IDs and queues the operation. `smbd_smb2_flush_send()` / `smbd_smb2_flush_recv()` implement the tevent wrapper. `struct smbd_smb2_flush_state` stores the SMB2 request and target `files_struct`; `smbd_smb2_flush_done()` receives `SMB_VFS_FSYNC_SEND()`.

Control flow: the handler verifies body size `0x18`, resolves the fsp with `file_fsp_smb2()`, creates a fake SMB1 request, rejects IPC, requires write/append access, permits directory flush only with add-file or add-subdirectory access, rejects handles without an I/O fd, and completes immediately when `strict sync` is disabled. With strict sync enabled it starts VFS async fsync, marks non-last compound requests async-internal so they complete synchronously, adds the request to the fsp AIO list, maps VFS errors, and emits a `0x04` response body.

State and persistence: no durable state is created. Temporary tevent state plus fsp AIO registration tracks outstanding work. Persistent effect is backend storage synchronization when strict sync is enabled.

Dependencies and integration: uses SMB2 packet helpers, `file_fsp_smb2()`, fake SMB1 request glue, access checks, `lp_strict_sync()`, VFS async fsync, AIO tracking, compound helpers, and Unix-to-NT error mapping.

Risks: directory flush permission rules are subtle. Non-last compound requests cannot go fully async. Handles without I/O fds must fail as invalid. Close must see outstanding fsync through AIO tracking.

Test signals: cover strict-sync on/off, file and directory flush, IPC flush, read-only handle denial, directory add permissions, invalid IDs, compound non-last flush, and close while fsync is pending.
