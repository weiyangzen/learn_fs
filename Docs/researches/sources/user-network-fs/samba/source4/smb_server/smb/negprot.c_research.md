# sources/user-network-fs/samba/source4/smb_server/smb/negprot.c

## Purpose
Implements SMB1 dialect negotiation for the source4 SMB server and the transition point from SMB1 negotiation to the SMB2 server. It parses the client's dialect list, chooses the most preferred dialect allowed by server min/max protocol settings, initializes negotiated capability state, prepares authentication challenge or GENSEC/SPNEGO bootstrap data, and rejects unsupported or repeated negotiation.

## Important APIs, Types, And Functions
- `smbsrv_reply_negprot()` is the wire entry point for `SMBnegprot`; it reads ASCII4 dialect strings using `req_pull_ascii4()`, checks `done_negprot`, and dispatches through `supported_protocols`.
- `supported_protocols[]` encodes preference order from `SMB 2.002` down to core dialects, with per-dialect reply functions and protocol levels.
- `reply_nt1()` builds the NT LM 0.12 negotiation response, including capabilities such as Unicode, status32, DFS, raw mode, large read/write, large files, extended security, and signing flags.
- `reply_smb2()` tears down SMB1 session/tcon/signing state, initializes SMB2 state, switches the packet callback to `smbsrv_recv_smb2_request`, and calls `smb2srv_reply_smb_negprot()`.
- `get_challenge()` creates `auth4_context` and obtains the 8-byte challenge for challenge-response authentication.
- Legacy reply helpers (`reply_corep`, `reply_coreplus`, `reply_lanman1`, `reply_lanman2`, `reply_nt1_orig`) serialize dialect-specific fixed fields, workgroup/server strings, raw-mode bits, and DOS/NT time formats.

## Control Flow
Negotiation is one-shot: `smbsrv_reply_negprot()` marks `done_negprot`, then loops through offered dialect strings. The server iterates its own preference table first, respecting `lpcfg_server_max_protocol()` and `lpcfg_server_min_protocol()`, so the selected dialect is the best mutually supported dialect. Legacy dialect handlers set `smb_conn->negotiate.protocol`, calculate raw-mode support from configuration, optionally allocate a challenge, and terminate the connection if mandatory signing is enabled for dialects that cannot sign. NT1 adds capability negotiation and either emits old-style challenge data or starts server-side GENSEC with SPNEGO/NTLMSSP. SMB2 selection discards SMB1-specific state and changes the receive path.

## State And Persistence
The file mutates connection-level negotiation state: `done_negprot`, `protocol`, `encrypted_passwords`, `auth_context`, `server_credentials`, `oid`, `max_recv`, `zone_offset`, and negotiated capability exposure. `auth_context` and `server_credentials` are deliberately reparented to the connection because session setup needs them after the request is gone. The large-file capability probe creates and unlinks a temporary lock-path file named `large_test.dat`.

## Dependencies And Integration Points
Depends on Samba loadparm, auth, credentials, GENSEC, packet, SMB2 server, and request serialization helpers from `request.c` and `srvtime.c`. It feeds `sesssetup.c` by preparing the auth context, challenge, selected OID, and server credentials. It feeds `receive.c` by setting the negotiated protocol/capabilities used by later dispatch and signing.

## Risks
Negotiation is security-sensitive because it advertises signing, raw mode, extended security, DFS, Unicode, and status-code behavior. `large_file_support()` performs a filesystem probe in the lock directory, so unusual permissions or filesystems can affect advertised large-file capability. NT1 negotiation sends the response with `smbsrv_send_reply_nosign()`, which is correct before signing setup but should remain explicit. Multiple negotiation attempts terminate the connection; tests should cover that behavior. Fallback from SPNEGO to raw NTLMSSP is compatibility-driven and depends on later session setup enforcing raw NTLMv2 policy.

## Test Signals
Useful tests include dialect preference under min/max protocol bounds, repeated negprot termination, mandatory-signing rejection for legacy dialects, NT1 capability flags for Unicode/status32/DFS/raw/large I/O, challenge generation with encrypted passwords, SPNEGO token and NTLMSSP fallback paths, and SMB2 negotiate handoff changing the packet callback and clearing SMB1 state.
