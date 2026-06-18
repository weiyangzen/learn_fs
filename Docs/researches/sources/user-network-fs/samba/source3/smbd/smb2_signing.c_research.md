# sources/user-network-fs/samba/source3/smbd/smb2_signing.c

Purpose: initializes server-side signing policy for a connection. For SMB2, signing is always permitted and desired by protocol behavior, so this file only records whether signing is mandatory according to smb.conf and delegates SMB1 signing initialization when the SMB1 server is compiled in.

Important API: `srv_init_signing(struct smbXsrv_connection *conn)` creates a temporary loadparm context with `loadparm_init_s3()`, calls `lpcfg_server_signing_allowed()` to populate `conn->smb2.signing_mandatory`, optionally calls `smb1_srv_init_signing()` under `WITH_SMB1SERVER`, unlinks the loadparm context, and returns whether initialization succeeded.

Control flow: connection setup calls this early in the SMB server lifecycle. If a loadparm context cannot be created, the function logs at debug level and returns false. Otherwise, SMB2 mandatory-signing state is obtained from configuration, SMB1 compatibility initialization is attempted when present, and the temporary context is removed from the connection talloc tree before returning.

State and persistence behavior: the only SMB2 state mutation is `conn->smb2.signing_mandatory`. No persistent database state is written. The loadparm context is temporary and explicitly unlinked. SMB1 initialization may mutate SMB1 signing state on the same connection when compiled.

Dependencies and integration points: depends on Samba loadparm helpers, the SMB signing configuration parser, `smb2_signing.h`, and optional SMB1 signing code. Later SMB2 negotiation and session setup code consume the mandatory signing flag when choosing security mode and signing requirements.

Risks: this small file is a policy bridge, so the main risk is interpreting smb.conf signing settings differently between SMB1 and SMB2. A failure to initialize loadparm rejects signing initialization entirely. Tests should ensure SMB2 mandatory signing follows `server signing` configuration, SMB2 signing remains allowed even when not mandatory, SMB1 builds still call SMB1 setup, non-SMB1 builds compile cleanly, and the temporary loadparm context does not leak under the connection.
