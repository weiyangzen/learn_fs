# sources/user-network-fs/samba/source3/smbd/smb1_reply.c

### Purpose
`smb1_reply.c` is the central SMB1 command-reply implementation for `smbd`. It converts decoded `struct smb_request` packets into SMB1 responses for tree connections, attribute operations, legacy directory search, file open/create/delete, raw and normal reads/writes, close/logoff/tree disconnect, printer commands, directory changes, rename/copy stubs, byte-range locking, and several obsolete multiplex commands. The file is compatibility-heavy: many branches explicitly preserve DOS/LANMAN/NT1 wire behavior, historical error mappings, and client quirks.

### Important APIs, Types, And Functions
- Handle validation helpers: `check_fsp_open()` verifies `connection_struct`, `files_struct`, connection identity, and VUID ownership; `check_fsp()` additionally rejects directories and pathref-only handles without I/O fds, then increments `fsp->num_smb_operations`.
- Path helper: `smb1_strip_dfs_path()` removes `\\server\share` style DFS prefixes after SMB1 path syntax conversion and clears `UCF_DFS_PATHNAME`.
- Tree and session lifecycle replies: `reply_tcon()`, `reply_tcon_and_X()`, `reply_ulogoffX()`, `reply_exit()`, `reply_close()`, and `reply_tdis()` create or tear down tcons, sessions, per-PID opens, individual opens, and tree connections.
- File and directory replies: `reply_checkpath()`, `reply_getatr()`, `reply_setatr()`, `reply_open()`, `reply_open_and_X()`, `reply_mknew()`, `reply_ctemp()`, `reply_unlink()`, `reply_mkdir()`, `reply_rmdir()`, and `reply_mv()` wrap path conversion and VFS calls.
- Search helpers: `make_dir_struct()`, `mask_match_search()`, `mangle_mask_match()`, `smbd_dirptr_8_3_match_fn()`, `get_dir_entry()`, `reply_search()`, `reply_fclose()`, `reply_findclose()`, and `reply_findnclose()` implement old 8.3 directory search and dptr cleanup.
- I/O replies: `reply_readbraw()`, `reply_lockread()`, `reply_read()`, `setup_readX_header()`, `reply_read_and_X()`, `reply_writebraw()`, `reply_writeunlock()`, `reply_write()`, `is_valid_writeX_buffer()`, `reply_write_and_X()`, `reply_lseek()`, `reply_flush()`, and `reply_writeclose()`.
- Locking replies: `reply_lock()`, `reply_unlock()`, `reply_lockingX()`, plus exported parsers `get_lock_pid()` and `get_lock_count()`.
- Printer replies: `reply_printopen()`, `reply_printclose()`, `reply_printqueue()`, and `reply_printwrite()` connect SMB1 print operations to Samba spool/open/write/query paths.

### Control Flow
Most handlers follow a common pattern: validate `wct`/buffer lengths, parse fields from `req->vwv` and `req->buf`, resolve handles or paths, enforce access and locking, call VFS or server subsystems, then build an SMB1 response with `reply_smb1_outbuf()` and `SSVAL`/`SIVAL` field writes. Path-based commands usually compute UCF flags, optionally extract snapshot tokens, call `smb1_strip_dfs_path()`, then use `filename_convert_dirfsp()` or related helpers before operating.

Tree connect flow parses service/password/device strings, finds or creates a tcon through `make_connection()`, sets `req->conn`, writes `smb_tid`, and returns optional NT1 extended response information such as share permissions, DFS, CSC, and extended-signature support. `reply_tcon_and_X()` also performs the SMB1 application-key setup on the first tree connect when a signing key exists, deriving extended signatures when requested.

Open/create flows map legacy open flags to NT create semantics, use `SMB_VFS_CREATE_FILE()`, defer on sharing violations where possible, fall back to FCB/DOS open compatibility for some opens, reject directory opens where the command expects files, set allocation size for `openX`, and report oplock grant bits in both core and extended forms.

Read paths split into raw, core, lockread, and AndX variants. Raw reads send direct NetBIOS-length-prefixed data and must return four zero bytes on many errors. `reply_read_and_X()` computes safe read sizes, tries scheduled AIO for smaller reads, and otherwise sends synchronously, using `sendfile` only when the packet is unchained, unencrypted, not signed, not an alternate stream, and the share/client policy allows it. Write paths similarly distinguish raw two-phase writes, core writes, zero-length truncation for `SMBwrite`, no-truncate zero writes for `SMBwriteX`, optional recvfile-style unread bytes, strict lock checks, and write-through sync.

Close, exit, ulogoff, and tree-disconnect paths are tevent-aware. If affected files have outstanding AIO, they mark relevant `fsp` objects as closing, enqueue waiters on each `fsp->aio_requests`, move the SMB request to a longer-lived context, and send the SMB response only after the wait queue drains.

### State And Persistence Behavior
The file mutates live SMB server state rather than persistent configuration. It creates and frees `smbXsrv_tcon`, `connection_struct`, `smbXsrv_session`, `files_struct`, directory pointer, oplock, and byte-range-lock state. Persistent filesystem changes occur through VFS create, write, truncate, mkdir, rmdir via delete-on-close, rename, unlink, timestamp updates, DOS attribute updates, and printer spool writes. Session state changes include marking sessions deleted on logoff, updating application/session keys during tree connect, clearing VUID caches on reauth elsewhere, and setting tree status to `NT_STATUS_NETWORK_NAME_DELETED` during disconnect. It also updates request/user-visible compatibility state such as current file position with `fh_set_pos()`, dptr resume status, close write times, oplock type, and `req->outbuf` ownership for async/direct-send paths.

### Dependencies And Integration Points
This file integrates with Samba's VFS (`SMB_VFS_CREATE_FILE`, `SMB_VFS_SENDFILE`, stat, lseek, delete-on-close), path conversion and DFS handling, `smbXsrv_session` and `smbXsrv_open` lookup, tcon management, locking/brlock async helpers, AIO queues, oplock helpers, signing state, encryption flags, IPC pipe handlers, printing/spoolss RPC, share configuration (`lp_*`), protocol profiling, and SMB1 packet construction/sending. It also depends on error translation helpers that map NTSTATUS to DOS/legacy errors, which is important for old dialect compatibility.

### Risks
- Wire length arithmetic is high risk. Many handlers parse client-supplied offsets and lengths; several comments call out CVE-2017-12163 protections. Any future change must preserve overflow and bounds checks around `smb_doff`, `numtowrite`, raw write data, print data, and search status blobs.
- Signing/encryption restrictions are security-sensitive. Raw reads/writes and `sendfile` are disabled when signing or sealing is active; relaxing this would break integrity/confidentiality guarantees.
- Async teardown is race-sensitive. `reply_ulogoffX`, `reply_exit`, `reply_close`, and `reply_tdis` rely on marking files closing, queueing AIO waits, and moving request ownership correctly.
- Compatibility branches intentionally return odd errors or behaviors for LANMAN/DOS/OS2/Win9x/NT clients. Seemingly cleaner NTSTATUS mappings or zero-length write semantics can regress client interoperability.
- Path conversion must preserve DFS, snapshot token, stream, POSIX pathname, and symlink/reparse-point behavior; inconsistent UCF flags can create security or namespace bugs.

### Test Signals
Relevant tests should include Samba torture coverage for SMB1 open/create/read/write, LARGE_READX, raw read/write disabled under signing/sealing, strict byte-range lock conflicts, delayed sharing violation deferral, old search/dptr resume and close, DFS path stripping, snapshot-token paths, print queue/write behavior, `BASE-SAMBA3ERROR` style DOS error mappings, `lock11` cancel behavior, and AIO close/logoff/tree-disconnect completion. Fuzz-style tests around `wct`, byte counts, offsets, and chained AndX forms are especially valuable.
