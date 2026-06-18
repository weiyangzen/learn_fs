# Research: sources/user-network-fs/samba/source4/smb_server/management.c

Purpose: exposes runtime SMB server session and tree-connect information over Samba IRPC.

Important APIs: `smbsrv_session_information()` counts `smb_conn->sessions.list`, allocates `smbsrv_session_info` records, and fills client IP, VUID, account/domain names, connect/auth/last-use times. `smbsrv_tcon_information()` does the same for `smb_conn->smb_tcons.list`, filling TID, share name, connect time, and last-use time. `smbsrv_information()` dispatches on `SMBSRV_INFO_SESSIONS` or `SMBSRV_INFO_TCONS`. `smbsrv_management_init()` registers the IRPC handler with `IRPC_REGISTER`.

State and dependencies: it reads live connection state but does not mutate sessions or tcons. It depends on IRPC, generated NDR types, tsocket address formatting, and auth session info fields.

Risks and test signals: comments mark this as debugging only; no access filtering is visible here beyond messaging context registration. Missing `session_info` would be unsafe if unfinished sessions reached the list exposed here. Signals are management queries returning accurate session/tcon counts and timestamps.
