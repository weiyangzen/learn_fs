# sources/user-network-fs/samba/source4/smb_server/smb2/sesssetup.c

## Purpose
This file implements SMB2 SESSION_SETUP and LOGOFF. It drives SPNEGO/GENSEC authentication, allocates and finalizes SMB2 sessions, activates signing when required, serializes security blobs, and schedules session destruction after logoff replies.

## Important APIs, Types, And Functions
Public entry points are `smb2srv_sesssetup_recv` and `smb2srv_logoff_recv`. Internal flow uses `smb2srv_sesssetup_backend`, `smb2srv_sesssetup_callback`, `smb2srv_sesssetup_send`, `smb2srv_logoff_backend`, `smb2srv_logoff_send`, and `smb2srv_cleanup_session_destructor`. The callback context carries the request, IO union, and target `smbsrv_session`.

## Control Flow
`smb2srv_sesssetup_recv` validates and decodes the SMB2 session setup body and security blob. The backend either starts a new GENSEC SPNEGO server context when the session id is zero, or resumes an in-progress setup session. New sessions get SMB2 tcon storage initialized. It rejects already-authenticated sessions and missing GENSEC state, sends `gensec_update_send`, disables packet receive while authentication is in flight, and stores signing requirements from client security mode. The async callback re-enables packet receive, receives the output token, obtains session info on success, finalizes the session, enables signing for authenticated users when required, and sends success or `MORE_PROCESSING_REQUIRED`. LOGOFF validates its tiny body and attaches a destructor that frees the session after the reply is sent.

## State And Persistence
Authentication state persists in `smbsrv_session`: `gensec_ctx`, `session_info`, vuid, tcon context, signing required/active flags, and timestamps managed by session helpers. LOGOFF frees the session and by extension session-owned tcons/handles. No disk state is directly changed.

## Dependencies And Integration Points
The file depends on GENSEC, auth session info, packet receive flow control, socket address capture, session allocation helpers, and SMB2 reply helpers. It is dispatched by `receive.c`; signing results are later consumed by `receive.c` and `smb2srv_send_reply`.

## Risks And Test Signals
Risks include receive being disabled during long authentication, subtle handling of partially established sessions, cleanup TODOs for open files on logoff, ignoring client `SIGNING_ENABLED`, and squashing auth statuses. Tests should cover multi-leg SPNEGO, wrong/resumed session ids, already-authenticated session setup, required signing activation, failed GENSEC update cleanup, logoff with open tcons, and no-reply internal paths.
