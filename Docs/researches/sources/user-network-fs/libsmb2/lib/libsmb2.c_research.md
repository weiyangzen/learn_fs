# sources/user-network-fs/libsmb2/lib/libsmb2.c

## Purpose

`libsmb2.c` is the high-level SMB2 client/server orchestration layer for libsmb2. It exposes async file, directory, metadata, notification, connection, disconnection, and server-loop operations by building SMB2 command request structures, queueing PDUs, and translating completion callbacks into the public callback contract. It also owns SMB2/SMB3 negotiation follow-up, session setup, tree connect, signing/encryption key derivation, SMB 3.1.1 pre-authentication hash updates, and a callback-dispatched SMB2 server path.

## Important APIs, Types, And Functions

The file defines local state carriers for async lifetimes: `struct connect_data` keeps connection callback data, server/share/user strings, UNC strings, auth context, and optional server context; `struct smb2fh` wraps file-id, current offset, EOF, and callback state; additional small structs (`read_data`, `write_data`, `stat_cb_data`, `trunc_cb_data`, `rename_cb_data`, `readlink_cb_data`, `notify_change_cb_data`) preserve callback state across compound requests.

Connection/session APIs include `smb2_connect_share_async`, `connect_cb`, `negotiate_cb`, `send_session_setup_request`, `session_setup_cb`, `tree_connect_cb`, `smb2_disconnect_share_async`, and `smb2_close_context`. These coordinate socket connect, dialect negotiation, SPNEGO/NTLMSSP or Kerberos auth, session-key extraction, signing/encryption key creation, optional tree connect, and teardown.

File and directory APIs include `smb2_opendir_async`, `smb2_readdir`, `smb2_seekdir`, `smb2_telldir`, `smb2_rewinddir`, `smb2_closedir`, `smb2_open_async`, `smb2_open_async_with_oplock_or_lease`, `smb2_close_async`, `smb2_fsync_async`, `smb2_pread_async`, `smb2_read_async`, `smb2_pwrite_async`, `smb2_write_async`, and `smb2_lseek`. Metadata and mutation APIs include `smb2_unlink_async`, `smb2_rmdir_async`, `smb2_mkdir_async`, `smb2_fstat_async`, `smb2_stat_async`, `smb2_statvfs_async`, `smb2_truncate_async`, `smb2_rename_async`, `smb2_ftruncate_async`, and `smb2_readlink_async`.

SMB3 security helpers include `smb2_derive_key`, `smb3_init_preauth_hash`, `smb3_update_preauth_hash`, and `smb2_create_signing_key`. Utility APIs include `smb2_get_max_read_size`, `smb2_get_max_write_size`, `smb2_get_file_id`, `smb2_fh_from_file_id`, `smb2_fd_event_callbacks`, `smb2_oplock_break_notify`, `smb2_decode_filenotifychangeinformation`, and `free_smb2_file_notify_change_information`.

The server side is handled by request callbacks such as `smb2_logoff_request_cb`, `smb2_tree_connect_request_cb`, `smb2_create_request_cb`, `smb2_read_request_cb`, `smb2_write_request_cb`, `smb2_ioctl_request_cb`, `smb2_query_directory_request_cb`, `smb2_query_info_request_cb`, `smb2_set_info_request_cb`, `smb2_session_setup_request_cb`, `smb2_negotiate_request_cb`, plus the listening loop `smb2_serve_port` and accept helper `smb2_serve_port_async`.

## Control Flow

Client share connection starts in `smb2_connect_share_async`: it stores server/share on the context, builds a `\\server\share` UNC in UTF-8 and UTF-16, then calls `smb2_connect_async`. `connect_cb` sends an SMB2 negotiate request with dialects based on configured version and encryption capability when applicable. `negotiate_cb` records server limits, dialect, cipher, and capabilities; enforces requested signing/encryption; auto-selects Kerberos or NTLMSSP from the SPNEGO mechanism list if the security mode was undefined; initializes auth data; and sends session setup. `session_setup_cb` handles `MORE_PROCESSING_REQUIRED` by sending the next auth token, otherwise extracts the session key for NTLMSSP or Kerberos, derives signing and encryption keys, validates a signed final session setup response when present, and issues tree connect unless passthrough mode suppresses it.

Directory enumeration opens a directory with `CREATE`, then loops `QUERY_DIRECTORY` until `SMB2_STATUS_NO_MORE_FILES`. `decode_dirents` converts file-id-full-directory-information records into linked `smb2_dirent_internal` entries with stat-like fields. Once enumeration is complete, a `CLOSE` command finalizes the directory handle and publishes the populated `smb2dir`.

File operations are single request/response flows for open, close, flush, read, write, fstat, and ftruncate. Read and write clamp transfer sizes to negotiated max sizes and available credits, then update `fh->offset` on successful completion. `smb2_lseek` is local-only state mutation based on `fh->offset` and `fh->end_of_file`.

Path operations such as unlink, mkdir, stat, statvfs, truncate, rename, and readlink are compound PDU flows. They typically `CREATE` the target, perform `QUERY_INFO`, `SET_INFO`, `IOCTL`, or `CLOSE` using `compound_file_id`, and aggregate statuses across callbacks before invoking the public callback.

Server mode starts with `smb2_serve_port`, which initializes defaults, binds/listens, accepts clients, allocates an SMB2 context per client, and drives active contexts through `select` and `smb2_service`. Request callbacks dispatch to `server->handlers` when present, build command replies or `STATUS_NOT_IMPLEMENTED`/related errors, set response message IDs to match requests, and queue replies. Negotiation chooses the highest mutually supported dialect, initializes preauth hashing, sets signing/encryption capabilities, emits SPNEGO negotiate data, and prepares the next expected PDU.

## State And Persistence Behavior

This file is almost entirely in-memory state. Persistent external effects are network I/O on SMB sockets and remote filesystem mutations requested through SMB2. `smb2_context` fields mutated here include fd, message/session/tree IDs, server/share/user, negotiated dialect and sizes, credits, signing/sealing flags, preauth hash, session/signing/encryption keys, security mode, client GUID, callbacks, active PDU pointers, and server association. `smb2fh` instances persist remote file IDs and local offsets until close/free. `smb2dir` stores a linked list of decoded directory entries until `smb2_closedir`.

Authentication state is owned indirectly through `connect_data->auth_data` and freed by `free_c_data` using NTLMSSP or Kerberos-specific destructors. `smb2_close_context` closes the fd, notifies fd-change callbacks, clears session/tree IDs, and frees the session key, but does not destroy the whole context. The server loop owns accepted contexts until disconnection, timeout, explicit close, or final cleanup.

## Dependencies And Integration Points

The implementation depends on libsmb2 internal protocol builders/parsers from `libsmb2-raw.h`, `libsmb2-private.h`, SMB2 command modules, `pdu.c`, socket helpers, Unicode conversion, timestamp conversion, error conversion, SPNEGO wrappers, NTLMSSP, optional Kerberos wrappers, signing, HMAC/SHA utilities, and portable endian helpers. Public callers integrate through `libsmb2.h` callbacks and through event-loop fd callbacks registered by `smb2_fd_event_callbacks`. Server users provide `struct smb2_server` handlers for authorization and command-specific filesystem behavior.

## Risks And Edge Cases

Many async allocation failure paths return without freeing previously allocated callback state or request context. Examples include some `smb2_pread_async`, `smb2_pwrite_async`, and `smb2_ftruncate_async` PDU creation failures where newly allocated state may leak. Compound request builders must keep stack request payloads valid only until PDU encoding; this relies on command builders copying input synchronously.

Credit clamping can reduce read/write count to `smb2->credits * 65536`; if credits are unexpectedly zero, requests may be built with zero-length transfers. Directory and file-notify decoders trust decoded offsets and converted names heavily; malformed server replies need fuzz coverage around offset arithmetic and recursive notify decoding.

Security-sensitive paths include signing/encryption key derivation, SMB 3.1.1 preauth hash sequencing, and signature verification during final session setup. A missed preauth update or wrong label/context length can break interoperability or weaken SMB3 validation. In `smb2_oplock_break_notify`, the lease branch uses `memset(&rep_lease, 0, sizeof(rep_oplock))`, which appears to clear using the wrong structure size and should be reviewed.

Server mode is functional but handler-dependent. Unimplemented handlers return protocol errors, and authorization/session establishment correctness depends on `server->handlers`. The select loop is single-threaded and iterates the global active-context list, so destruction during iteration is handled carefully in some places but remains a high-risk area for lifecycle bugs.

## Test Signals

Useful tests include connection negotiation across SMB2.0.2, SMB2.1, SMB3.0, SMB3.0.2, and SMB3.1.1 with signing required, encryption requested, passthrough mode, NTLMSSP, and Kerberos builds. File API tests should cover open flag mapping, lease/oplock create contexts, offset updates after read/write, EOF reads, max-read/write clamping, fstat/stat/statvfs decoding, truncate and rename compounds, readlink on symlink and non-reparse targets, and directory enumeration over multi-response directories. Server tests should exercise each handler dispatch, unsupported command responses, negotiate/session setup state transitions, anonymous versus password auth, tree connect/disconnect cleanup, and fd event notifications. Fuzzing should target directory entry decoding, notify-change decoding, create/query/set compound replies, and SMB3 preauth/signature validation.
