# File Research: sources/os/linux/linux/fs/smb/server/mgmt/user_session.h

This header defines ksmbd’s per-user SMB session model and the public session-management API used by the SMB2/SMB3 server path.

Key structures:
- `struct channel` binds a `ksmbd_conn` to an SMB3 signing key for multichannel-capable sessions.
- `struct preauth_session` stores SMB 3.1.1 preauthentication hash state before a full session is established.
- `struct ksmbd_session` is the central authenticated-session object. It tracks session id, dialect, client GUID, user, sequence number, signing/encryption flags, state, preauth hash, session key, channel xarray, tree-connect xarray and ID allocator, RPC handle xarray, SMB3 encryption/decryption/signing keys, file table, activity time, procfs entry, refcount, and locks.

Important exported operations:
- Session lifecycle: `ksmbd_smb2_session_create`, `ksmbd_session_destroy`, `ksmbd_session_register`, `ksmbd_sessions_deregister`.
- Lookup paths: per-connection, global/all-session, slowpath, and raw `__session_lookup`.
- Preauth: `ksmbd_preauth_session_alloc`, `ksmbd_preauth_session_lookup`.
- Tree-connect IDs: `ksmbd_acquire_tree_conn_id`, `ksmbd_release_tree_conn_id`.
- RPC handles: `ksmbd_session_rpc_open`, `ksmbd_session_rpc_close`, `ksmbd_session_rpc_method`.
- Refcounting: `ksmbd_user_session_get`, `ksmbd_user_session_put`.

Concurrency/lifetime notes:
- `chann_lock`, `tree_conns_lock`, and `rpc_lock` protect mutable per-session containers.
- `atomic_t refcnt` makes session lifetime explicit across request dispatch and async paths.
- Procfs session visibility is compiled under `CONFIG_PROC_FS`.

Role in this group:
- `server.c` obtains/releases sessions while handling requests.
- `proc.c` initializes procfs, while session-specific proc entries are declared here and implemented in session management code.
- `ntlmssp.h` provides constants and packet structures needed to authenticate and fill session keys.
