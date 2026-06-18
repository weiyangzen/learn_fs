# sources/user-network-fs/samba/source4/smb_server/smb/sesssetup.c

## Purpose
Implements backend authentication and authorization for SMB1 session setup variants. It handles legacy LM response, NT1 bare NTLM response, and SPNEGO/GENSEC exchanges, creates SMB session objects, logs successful non-SPNEGO authz events, derives session info, and enables SMB signing after authentication.

## Important APIs, Types, And Functions
- `smbsrv_sesssetup_backend()` dispatches `RAW_SESSSETUP_OLD`, `RAW_SESSSETUP_NT1`, and `RAW_SESSSETUP_SPNEGO`.
- `sesssetup_old()` and `sesssetup_nt1()` build `auth_usersupplied_info` and call `auth_check_password_send()`.
- `sesssetup_old_send()` and `sesssetup_nt1_send()` receive auth results, generate `auth_session_info`, allocate `smbsrv_session`, mark setup complete, and set the VUID.
- `sesssetup_spnego()` starts or resumes a GENSEC context and disables packet receive while async auth is in flight.
- `sesssetup_spnego_send()` consumes GENSEC output, obtains session info and session key, and finalizes the SMB session.
- `smbsrv_not_spengo_sesssetup_authz_log()` logs successful bare-NTLM authorization events.

## Control Flow
The parser in `reply.c` fills a `union smb_sesssetup`; this file handles authentication. Old and NT1 flows gather remote/local socket addresses, workstation name, account/domain, and password response blobs, then submit an async auth check. On success they generate session info, create a frontend session, log authz, mark the session valid for normal use, set `req->session` for possible AndX tree connect, and return through `smbsrv_reply_sesssetup_send()`. NT1 also configures signing using the session key and NT response. SPNEGO creates a temporary session with a GENSEC context on first leg, updates it with the input token, returns `MORE_PROCESSING_REQUIRED` as needed, and finalizes when GENSEC completes.

## State And Persistence
Successful session setup sets `smb_conn->negotiate.done_sesssetup`, reparents the session to the connection, stores `session_info` on the session, and may establish the connection signing key. In-progress SPNEGO sessions are lookupable by VUID before final session info exists. Packet receive is disabled during async SPNEGO processing and re-enabled in the callback.

## Dependencies And Integration Points
Depends on auth4, GENSEC, tsocket address APIs, packet receive control, loadparm raw NTLMv2 policy, and session helpers. It consumes negotiation state prepared by `negprot.c`, especially challenge/auth context and selected GENSEC OID, and returns serialized responses through `reply.c`.

## Risks
This is a security-critical path. Raw NTLMv2 is rejected unless `raw_ntlmv2_auth` allows it, while SPNEGO is preferred when negotiated. The old-style path appears to pass `req->smb_conn->negotiate.auth_context` to `auth_check_password_send()` even when a local `state->auth_context` was created, which is worth regression attention. SPNEGO packet receive suppression prevents EOF/reentrancy crashes but must always re-enable. Partial SPNEGO sessions must be freed on terminal failure.

## Test Signals
Test successful and failed old/NT1 auth, anonymous or missing server credentials fallback, raw NTLMv2 rejection policy, signing setup after NT1 and SPNEGO, SPNEGO multi-leg `MORE_PROCESSING_REQUIRED`, invalid VUID continuation, logoff of partially authenticated sessions, socket address failures, packet receive disable/enable balance, and AndX tree connect immediately after session setup.
