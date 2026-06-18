<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap_gensec_bind.c -->
# sources/user-network-fs/samba/source3/lib/tldap_gensec_bind.c

## Purpose
This file implements SASL `GSS-SPNEGO` LDAP bind using Samba GENSEC. It drives the token exchange over `tldap_sasl_bind_send` and optionally wraps the LDAP connection in a signed or sealed GENSEC tstream after authentication.

## Important APIs, types, and functions
`struct tldap_gensec_bind_state` carries the event context, LDAP context, credentials, target service/host/principal, loadparm context, requested GENSEC features, GENSEC security context, current NTSTATUS, and input/output tokens. `tldap_gensec_bind_send`, `tldap_gensec_bind_recv`, and synchronous `tldap_gensec_bind` form the public API. Internal callbacks `tldap_gensec_update_next`, `tldap_gensec_update_done`, and `tldap_gensec_bind_done` alternate between local GENSEC updates and LDAP SASL bind round trips.

## Control flow
Send initializes GENSEC, sets credentials and target identity, applies TLS channel bindings when the LDAP context is already on TLS, requests features, and starts the `GSS-SPNEGO` mechanism. Each GENSEC output token is sent as SASL credentials with empty DN and mechanism `GSS-SPNEGO`. Server SASL credentials become the next GENSEC input. Completion requires both LDAP success and GENSEC success; `TLDAP_SASL_BIND_IN_PROGRESS` and `NT_STATUS_MORE_PROCESSING_REQUIRED` keep the loop alive. Receive verifies requested signing/sealing features and, when negotiated, steals the GENSEC context under the LDAP context and installs a GENSEC tstream over the plain stream.

## State and persistence behavior
Authentication state is transient until receive succeeds. If signing or sealing is negotiated, the GENSEC context persists as a child of the LDAP context because the stream wrapper depends on it. Token blobs are explicitly freed between iterations.

## Dependencies and integration points
It integrates `tldap.c` SASL bind APIs with `auth/gensec`, credentials, `loadparm`, `gensec_tstream`, and TLS channel binding data from `tldap_tls_channel_bindings`.

## Risks and edge cases
The code refuses GENSEC sign/seal over TLS to avoid double wrapping and policy confusion. TLS channel binding setup can fail and is treated as LDAP operations error. A first GENSEC success with no output is treated as invalid credentials. Feature verification after bind is important because the server may authenticate without honoring requested sign/seal.

## Test signals
Coverage is mostly integration-level through LDAP authentication paths that request Kerberos/NTLM SPNEGO, sign/seal, or TLS channel binding. Useful tests should verify TLS plus channel bindings, refusal of sign/seal over TLS, and stream replacement after negotiated wrapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap_gensec_bind.c -->
