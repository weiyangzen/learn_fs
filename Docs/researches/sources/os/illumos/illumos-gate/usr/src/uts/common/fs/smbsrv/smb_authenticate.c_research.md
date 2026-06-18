# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_authenticate.c

Implements SMB authentication support for SMB1 and SMB2 session setup.

Key behavior:
- Old-style SMB1 authentication creates a user, opens an auth socket, sends client info, sends legacy logon request, then imports an auth token.
- Extended-security authentication creates or finds a logging-on user across multi-step session setup, forwards security blobs to userland auth service, handles continue/done/error replies, and imports the final token.
- SMB 3.1.1 updates preauth hash across session setup messages and stores per-user preauth hash values.
- Token import decodes XDR token data, creates credentials, translates privileges, logs on the SMB user, initializes SMB3 encryption keys, and initializes signing for non-anonymous/non-guest users.
- Auth socket communication is cancellable through request state transitions and `smb_authsock_cancel()`.
- Auth socket concurrency is threshold-limited, uses send/receive timeouts, and connects to an AF_UNIX smbd auth service socket.
- Provides send/recv wrappers that require exact message sizes and map failures to RPC/NT statuses.
- Closes auth sockets and releases threshold slots on user cleanup.

Important dependencies:
- Userland auth protocol: `smb_lsa_msg_hdr_t`, `LSA_MTYPE_*`, XDR helpers.
- User/session management: `smb_user_new`, `smb_user_logon`, `smb_user_logoff`, `smb_session_lookup_uid_st`.
- Credential/token helpers: `smb_cred_create`, `smb_token_xdr`, `smb_token_query_privilege`.
- Security setup: `smb2_sign_begin`, `smb_sign_begin`, `smb3_encrypt_begin`, `smb31_preauth_sha512_calc`.

Notable details:
- Authentication service communication errors are expected to be rare but can occur under auth service saturation.
- Guest/anonymous users still get encryption state initialized because Windows may send encrypted requests for them.
