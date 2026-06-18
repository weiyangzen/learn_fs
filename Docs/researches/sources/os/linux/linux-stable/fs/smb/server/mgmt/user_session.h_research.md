# File Research: sources/os/linux/linux-stable/fs/smb/server/mgmt/user_session.h

This header defines ksmbd’s per-user SMB session state and declares the session-management API used by SMB2/SMB3 authentication, tree-connect handling, multichannel, RPC handles, and `/proc` session reporting.

Key definitions:
- `CIFDS_SESSION_FLAG_SMB2`: session flag bit for SMB2-family sessions.
- `PREAUTH_HASHVALUE_SIZE`: SMB 3.1.1 preauthentication hash size, 64 bytes.
- `struct channel`: per-channel signing key and associated `ksmbd_conn`, used for SMB3 multichannel.
- `struct preauth_session`: preauthentication hash value, session id, and list node.
- `struct ksmbd_session`: central session object containing:
  - session id, dialect, client GUID, user pointer, sequence number, flags
  - signing/encryption booleans and session state
  - preauth hash pointer and NTLM/CIFS session key
  - hash/list linkage, channel xarray, tree connection xarray/IDA, RPC handle xarray
  - SMB3 encryption/decryption/signing keys
  - per-session file table, last activity timestamp, locks, optional proc entry, refcount

Inline helpers:
- `test_session_flag()`
- `set_session_flag()`
- `clear_session_flag()`

Declared APIs:
- Session lifecycle: `ksmbd_smb2_session_create()`, `ksmbd_session_destroy()`.
- Session lookup and registration: `ksmbd_session_lookup*()`, `__session_lookup()`, `ksmbd_session_register()`, `ksmbd_sessions_deregister()`.
- Session replacement: `destroy_previous_session()`.
- SMB 3.1.1 preauth sessions: `ksmbd_preauth_session_alloc()`, `ksmbd_preauth_session_lookup()`.
- Tree connection ID allocation: `ksmbd_acquire_tree_conn_id()`, `ksmbd_release_tree_conn_id()`.
- Named-pipe/RPC tracking: `ksmbd_session_rpc_open()`, `ksmbd_session_rpc_close()`, `ksmbd_session_rpc_method()`.
- Refcounting: `ksmbd_user_session_get()`, `ksmbd_user_session_put()`.
- Proc integration: `create_proc_sessions()`.

Concurrency and ownership:
- `ksmbd_session` uses `rw_semaphore` locks for channel, tree connection, and RPC state.
- `xarray` containers hold channels, tree connections, and RPC handles.
- `atomic_t refcnt` protects lifetime across request processing and async paths.

Risk areas:
- Session refcounting is security-critical; premature put or missing get can turn request/session lookup paths into use-after-free risks.
- Multichannel state depends on `ClientGUID`, channel xarray contents, and per-channel signing keys staying consistent.
- Preauth hash state is part of SMB 3.1.1 authentication integrity; changes affect downgrade and session setup behavior.
