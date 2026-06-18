# sources/user-network-fs/samba/source4/auth/gensec/gensec_gssapi.c

## Purpose

This file implements Samba's real GSSAPI-backed GENSEC Kerberos mechanisms. It registers SPNEGO-over-GSSAPI, Kerberos-over-GSSAPI, and SASL GSSAPI mechanisms, handles client/server security context negotiation, enforces optional channel binding, negotiates SASL security strength, exposes wrap/unwrap and packet sign/seal operations, extracts session keys and PAC/session information, and tracks credential expiry.

## Important APIs, Functions, And State

The public entry point is `gensec_gssapi_init(TALLOC_CTX *ctx)`, which registers `gssapi_spnego`, `gssapi_krb5`, and `gssapi_krb5_sasl` security ops. Major internal functions are `gensec_gssapi_start()`, `gensec_gssapi_server_start()`, `gensec_gssapi_sasl_server_start()`, `gensec_gssapi_client_creds()`, `gensec_gssapi_client_start()`, `gensec_gssapi_sasl_client_start()`, `gensec_gssapi_update_internal()`, update send/recv wrappers, `gensec_gssapi_wrap()`, `gensec_gssapi_unwrap()`, packet seal/unseal/sign/check helpers, `gensec_gssapi_have_feature()`, `gensec_gssapi_expire_time()`, `gensec_gssapi_session_key()`, `gensec_gssapi_session_info()`, `gensec_gssapi_sig_size()`, and `gensec_gssapi_final_auth_type()`.

State lives in `struct gensec_gssapi_state` from `gensec_gssapi.h`: GSS context, server/client names, requested and negotiated flags, delegated credential handle, expiry time, selected mechanism OID, input channel bindings, Kerberos context, client/server credential containers, SASL mode and stage, SASL protection bits, max wrap buffer size, exchange count, cached signature size, and target principal string.

## Control Flow

Start-up allocates state, copies optional channel bindings from `gensec_security`, chooses requested GSS flags from settings and wanted GENSEC features, selects SPNEGO or Kerberos OID based on DCERPC auth type, initializes a Samba Kerberos context, and sets defaults for credentials and SASL state. Heimdal builds also set default realm and disable DNS canonicalization.

Client update flow first obtains client GSS credentials, builds or imports the target service principal, and calls `gss_init_sec_context()`. MIT builds include a fallback path for external trusts: they first try the client realm and on `KRB5KDC_ERR_S_PRINCIPAL_UNKNOWN` can derive the server realm from the hostname and retry. Heimdal builds temporarily route KDC traffic through Samba's event-aware send function.

Server update flow calls `gss_accept_sec_context()` with server credentials and optional channel bindings, captures client name and delegated credentials, and maps missing or bad channel-binding flags to `NT_STATUS_BAD_BINDINGS` when bindings are required. Successful non-SASL negotiation moves directly to `STAGE_DONE`; SASL mechanisms move to `STAGE_SASL_SSF_NEG` for a second negotiation.

SASL negotiation wraps a four-byte proposal/acceptance token with GSS. The server advertises supported `NEG_SEAL`, `NEG_SIGN`, and `NEG_NONE` plus max wrap size. The client intersects that with requested GENSEC features and returns accepted protection and max size. The server validates the accepted bits and both sides finish in `STAGE_DONE`.

## State And Persistence

The GSS context and names persist only for the lifetime of the `gensec_security` talloc tree. The destructor releases delegated credentials, deletes the GSS security context, and releases GSS names. Delegated client credentials may be transferred into `session_info->credentials`, after which the state clears its handle to avoid double release. Expiry time is stored as NTTIME after successful negotiation. No disk persistence is performed.

## Dependencies And Integration Points

The implementation depends on system GSSAPI, Samba Kerberos wrappers, credential containers, GENSEC registration, tevent, tsocket channel binding data, PAC utilities, session generation, loadparm settings, and DCE/RPC auth type constants. It integrates with SMB/RPC signing and sealing through GENSEC ops, with LDAP SASL through the `sasl_name = "GSSAPI"` mechanism, with SPNEGO through the SPNEGO OID, and with authorization through `gssapi_obtain_pac_blob()` plus `gensec_generate_session_info_pac()`.

## Risks And Edge Cases

Security-sensitive risks include incorrect channel-binding enforcement, accepting a context without integrity when signing/session key features are required, mishandling SASL max wrap sizes, failing to release GSS buffers/names/contexts, or misreporting negotiated features. Kerberos realm fallback differs between MIT and Heimdal. Old encryption types intentionally suppress `GENSEC_FEATURE_NEW_SPNEGO`, so changes to key type logic can affect compatibility. Delegation handling must avoid both credential leaks and double frees.

## Test Signals

Useful signals include Kerberos client/server GENSEC handshakes, SPNEGO handshakes, SASL GSSAPI LDAP binds with sign/seal/none options, channel-binding required and optional cases, external trust principal fallback on MIT, delegated credential sessions, PAC-backed and no-PAC session info generation, packet sign/check and seal/unseal tests, max wrap size limits, expired credential handling, and final auth type/session key extraction.
