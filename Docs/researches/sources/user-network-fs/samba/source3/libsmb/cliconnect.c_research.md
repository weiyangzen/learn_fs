# sources/user-network-fs/samba/source3/libsmb/cliconnect.c

## Purpose
`cliconnect.c` implements source3 client connection setup and teardown for SMB clients. It covers credential object construction, SMB1 and SMB2 session setup, SPNEGO/GENSEC negotiation, guest and anonymous setup, tree connect/disconnect, transport socket creation, protocol negotiation, SMB1 Unix-extension encryption setup, full connection orchestration through tree connect, raw legacy tree connect, and helper IPC/master-browser connection routines.

The file is the bridge between high-level `libsmb` connection APIs and lower layers such as name resolution, socket transport, `smbXcli` negotiation, SMB1 request builders, SMB2 session/tree connect functions, GENSEC authentication, signing, and encryption policy.

## Important APIs, Types, And Functions
`cli_session_creds_init()` builds a `cli_credentials` object from username/domain/realm/password options. It handles empty-password anonymous logic, `DOMAIN\user`, `DOMAIN/user`, and winbind-separator username forms, principal-to-account conversion, Kerberos required/disabled policy, NTLM ccache features, plaintext password setting, and NT-hash password parsing.

Session setup helpers include `cli_session_setup_guest_create/send/recv()` for NT1 guest setup, `cli_sesssetup_blob_send/recv()` for chunked SPNEGO token exchange over SMB1 extended security or SMB2 session setup, `cli_session_setup_gensec_send/recv()` for the local/remote GENSEC handshake, `cli_session_setup_spnego_send/recv()` as a SPNEGO wrapper, and `cli_session_setup_creds_send/recv()` plus synchronous `cli_session_setup_creds()` as the main credential-based session setup API. `cli_session_setup_anon()` constructs anonymous credentials and delegates to the main session setup path.

Connection teardown and tree APIs include `cli_ulogoff()`, `cli_tcon_andx_create/send/recv()`, `cli_tcon_andx()`, `cli_tree_connect()`, `cli_tree_connect_creds()`, `cli_tdis()`, and `cli_raw_tcon()`. These select SMB2 logoff/tree disconnect, SMB1 `ulogoffX`, SMB1 `tconX`, or old raw `SMBtcon` based on negotiated protocol and server capabilities.

Transport and negotiation APIs include `cli_connect_nb()`, private `cli_connect_sock_send/recv()`, private `cli_connect_nb_send/recv()`, `cli_start_connection()`, and private `cli_start_connection_send/recv()`. They resolve names when needed, connect through configured SMB transports, create `cli_state`, choose min/max protocol from client settings and flags, optionally add SMB2 POSIX negotiate contexts, call `smbXcli_negprot_send()`, and raise SMB2 credits after successful negotiation.

Encryption/full-connect APIs include `cli_smb1_setup_encryption()`, private `cli_smb1_setup_encryption_blob_send/recv()`, private `cli_smb1_setup_encryption_send/recv()`, `cli_full_connection_creds_send/recv()`, and synchronous `cli_full_connection_creds()`. Full connect performs transport connection, negotiation, session setup, optional anonymous fallback, encryption activation, optional IPC$ setup for SMB1 Unix encryption, and final tree connect.

Browser/IPC helpers include private `get_ipc_connect()` and public `get_ipc_connect_master_ip()`, which force SMB1 IPC connections for legacy browsing/master-browser discovery and fall back from IP address to NetBIOS name status when needed.

## Control Flow
Credential initialization starts by creating a `cli_credentials` object, loading source3 parameters, normalizing username/domain/principal fields, applying Kerberos policy, optionally enabling NTLM ccache, then setting password, NT hash, or Kerberos ccache. Failure releases the partially built credential object.

The main session setup decision in `cli_session_setup_creds_send()` is protocol and capability driven. SMB2 and SMB1 extended-security connections use SPNEGO/GENSEC. Older SMB1 paths choose anonymous, plaintext, LM/NTLM, or NTLMv2 response construction depending on security mode, protocol, and configured client authentication policy. NT1 session setup activates signing and validates the signed response when a session key is available. LM21 setup only updates server strings.

The GENSEC session setup state machine alternates local token generation (`gensec_update_send/recv()`) and remote token submission (`cli_sesssetup_blob_send/recv()`). It tracks `local_ready` and `remote_ready`, detects invalid extra blobs, special-cases guest sessions that cannot complete a session-key handshake, extracts the session key, and installs it in SMB2 or SMB1 session state. For SMB2/SMB3, it can also dump signing/application/encryption/decryption keys when debug encryption is enabled.

Tree connect control flow selects by negotiated protocol. SMB2 builds a UNC string and calls `smb2cli_tcon_send()`. LANMAN1 and newer SMB1 uses `tconX`, including share-level password handling and optional extended-signature support. Very old SMB uses raw `SMBtcon`. Tree disconnect and logoff similarly split SMB2 direct helpers from SMB1 request/response state machines.

Connection startup is layered. `cli_connect_sock_send()` resolves or accepts a socket address and calls `smbsock_any_connect_send()`. `cli_connect_nb_send()` parses optional `host#type`, creates `cli_state` around the connected transport, and returns it. `cli_start_connection_send()` selects protocol bounds from global client settings and flags, optionally requests SMB2 POSIX extensions, connects, negotiates, and configures SMB2 credits.

Full connection orchestration is a linear tevent chain with cleanup ownership. It starts transport/protocol negotiation, performs session setup, optionally retries with anonymous credentials if requested, activates encryption according to credential policy, optionally probes SMB1 Unix extension encryption through temporary IPC$, then performs the requested share tree connect. The state destructor shuts down partial `cli_state` objects unless ownership is moved out by the receive function.

## State And Persistence
Persistent-in-process state is concentrated in `cli_state`: server OS/type/domain strings, UID/session state, SMB1 or SMB2 session objects, tree connect objects, share/device strings, signing/encryption state, negotiated protocol/capabilities, and transport references. This file mutates that state after session setup, tree connect, tree disconnect, logoff, encryption setup, and negotiation.

Secrets are handled through `cli_credentials` and transient `DATA_BLOB`s. `cli_session_setup_creds_cleanup()` clears password/session-key blobs when the request is received. GENSEC state destructors free auth state and clear session keys. SMB1 encryption setup moves a `smb_trans_enc_state` into the connection and marks encryption on. SMB2 session setup installs session keys in the SMB2 session object.

Network persistence is limited to remote session and tree state. Session setup authenticates and allocates a server session; logoff invalidates it. Tree connect allocates a server tree id; tree disconnect releases it. Full connection may temporarily connect to IPC$ to negotiate SMB1 Unix transport encryption, then disconnect it before connecting the target share.

## Dependencies And Integration Points
The file depends on source3 client state (`client.h`), generated and hand-written `libsmb` prototypes, ADS status mapping, NetBIOS namequery/nmblib, socket transport connection helpers, `smbXcli_base`, SMB1/SMB2 session and tree connect primitives, GENSEC/auth_generic/NTLMSSP credentials, source3 loadparm settings, SMB sealing/encryption helpers, tevent NTSTATUS helpers, and SMB2 negotiate context support.

It integrates high-level public connection APIs with authentication policy (`client plaintext auth`, `client lanman auth`, `client ntlmv2 auth`, `client use spnego`, Kerberos state), signing/encryption settings from credentials, configured SMB transports, min/max protocol settings, IPC-specific protocol settings, POSIX negotiate-context requests, legacy browser code, and SMB1 Unix extension encryption.

## Risks And Test Signals
Authentication downgrade and policy handling are the main security risks. Tests should cover Kerberos-required against non-SPNEGO servers, plaintext/LM auth disabled paths, NTLMv2 without SPNEGO policy rejection, anonymous fallback with encryption desired versus required, guest sessions with signing required, and ccache/no-password handling.

State-machine correctness is critical. SPNEGO/GENSEC should be tested with multi-leg Kerberos and NTLMSSP, guest success, malformed extra blobs, failed final signatures, SMB2 session allocation cleanup on failure, and session key installation. SMB1 encryption uses heuristics because the server may return OK before it is actually ready; tests should include Unix-extension encryption supported, unsupported, desired, and required cases.

Connection and tree tests should cover name resolution versus pre-supplied addresses, `host#type` parsing, NetBIOS/IP fallback, transport list ordering, protocol min/max flags forcing or disabling SMB1, POSIX negotiate-context request, SMB2 credit initialization, share-level password behavior, raw legacy tree connect, and cleanup of partially connected `cli_state` objects on every failure edge.

Parsing and memory ownership also need regression coverage. Session setup server strings are pulled from SMB byte areas and defaulted to empty strings. `cli_state_update_after_sesssetup()` only fills empty fields, so tests should confirm server metadata is not overwritten unintentionally. Blob cleanup should be checked with leak and secret-zeroing tools. Tcon paths should verify `cli->share`, `cli->dev`, SMB1 tcon IDs, optional support flags, and SMB2 tcon ownership after success and failure.
