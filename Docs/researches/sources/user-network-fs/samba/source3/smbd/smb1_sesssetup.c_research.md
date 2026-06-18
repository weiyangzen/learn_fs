# sources/user-network-fs/samba/source3/smbd/smb1_sesssetup.c

### Purpose
`smb1_sesssetup.c` handles SMB1 `SMBsesssetupX` authentication. It supports extended-security SPNEGO and legacy plaintext/NTLM response flows, creates and updates `smbXsrv_session` records, installs session/auth info, negotiates or activates SMB1 signing, registers homes shares, updates client capability state, and builds the SMB1 session setup response.

### Important APIs, Types, And Functions
- `push_signature()` appends native OS, Samba version, and workgroup strings to session setup replies.
- `reply_sesssetup_and_X_spnego()` implements the extended-security path using GENSEC/SPNEGO. It accepts continuation on an existing VUID, creates or finds a session auth context, calls `gensec_update()`, finalizes `auth_session_info`, creates SMB1 signing keys, sets expiration for dynamic reauth, claims and updates the session, and returns a token plus server signature strings.
- `shutdown_other_smbds()` and `setup_new_vc_session()` implement the optional `VC == 0` behavior that can signal other smbd processes from the same client IP to shut down when `reset on zero vc` is enabled.
- `struct reply_sesssetup_and_X_state` owns temporary authentication material; its destructor clears LM/NT/plaintext blobs.
- `reply_sesssetup_and_X()` is the exported command handler. It detects SPNEGO vs legacy forms, parses password blobs and user/domain/client strings, prepares `auth_usersupplied_info`, checks credentials, creates the session, installs keys and auth state, activates signing where possible, and updates the SMB UID fields.

### Control Flow
At entry, the handler records client signing flags and calls `smb1_srv_set_signing_negotiated()`. If the packet is a 12-word extended-security request and SPNEGO was negotiated, it optionally runs zero-VC cleanup and delegates to `reply_sesssetup_and_X_spnego()`.

The legacy path branches by negotiated protocol. Pre-NT1 packets remove 32-bit status support and parse a single password blob plus username. NT1 packets parse LM and NT response lengths, client capabilities, username, domain, native OS, native LANMAN, and optional primary-domain strings. The code includes compatibility repairs for old clients that misreport plaintext password lengths. It then handles anonymous, encrypted NTLM response, and plaintext authentication setup paths, calls `auth_check_password_session_info()`, and builds the response.

On success, both SPNEGO and legacy paths create or update an `smbXsrv_session`, configure SMB1 signing algorithm metadata, create a signing key from the auth session key, create or preserve the SMB1 application key, set `auth_session_info`, increment auth sequence numbers, register `[homes]` for real users, call `session_claim()` and `smbXsrv_session_update()`, adjust `xconn->smb1.sessions.max_send` on first session setup, reload services, and set response VUID/action fields.

### State And Persistence Behavior
The file mutates connection-wide client capability state (`global_client_caps`, common flags2, remote architecture), SMB1 signing negotiation/activation state, `xconn->smb1.sessions.done_sesssetup` and `max_send`, server user count, current user info, session records, session auth contexts, auth sequence numbers, auth time, expiration time, signing/application key blobs, and `[homes]` share registration. It can send process shutdown messages to other smbd instances for zero-VC reset. Sensitive temporary credential blobs are cleared in the state destructor and session keys are cleared or moved after derivation.

### Dependencies And Integration Points
This file integrates with auth4 and GENSEC, NTLM challenge creation, `smbXsrv_session` create/update/claim/auth APIs, SMB signing key creation, SMB1 signing activation, server messaging, remote architecture detection, loadparm workgroup/version/share reload behavior, and profile auth counters. It is upstream of `smb1_service.c` because successful authenticated sessions populate `session->homes_snum` for `[homes]` tree connects.

### Risks
- Credential parsing is wire-exposed and highly compatibility-sensitive. Password lengths, Unicode/plaintext handling, and capability-driven status flags must remain bounded and historically compatible.
- SPNEGO continuation reuses sessions and pending auth; incorrect state clearing can break reauth or leak partial auth contexts.
- Session key/application key handling is security-critical. The code intentionally clears raw session keys and defers/derives application keys differently in SPNEGO vs legacy paths.
- Signing negotiation depends on both client flags and server policy; incorrect activation can either reject clients or leave signed-required sessions unsigned.
- `VC == 0` reset can signal other smbd processes; address matching and configuration gating must remain conservative.

### Test Signals
Important coverage includes SMB1 SPNEGO multi-leg authentication, legacy encrypted NTLM, plaintext fallback when configured, anonymous/guest logons, signing-required and signing-optional clients, first-session `max_send` setup, dynamic reauth expiration, `[homes]` registration, session update/claim failure handling, malformed password lengths, Unicode/plaintext password variants, zero-VC reset behavior, and auth profile success/failure counters.
