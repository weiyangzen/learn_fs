<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap_tls_connect.c -->
# sources/user-network-fs/samba/source3/lib/tldap_tls_connect.c

## Purpose
`tldap_tls_connect.c` upgrades an existing plain tldap connection to TLS using Samba's `tstream_tls_connect` infrastructure.

## Important APIs, types, and functions
`struct tldap_tls_connect_state` stores event context, LDAP context, and TLS parameters. Public APIs are `tldap_tls_connect_send`, `tldap_tls_connect_recv`, and synchronous `tldap_tls_connect`. The implementation callback is `tldap_tls_connect_crypto_done`.

## Control flow
The send function validates that the LDAP connection is still usable, rejects attempts to start TLS after a GENSEC stream is active, obtains the plain tstream, and starts the TLS connect subrequest. On completion, the callback receives the TLS stream and calls `tldap_set_tls_tstream`, which makes it the active LDAP transport.

## State and persistence behavior
Successful upgrade stores the TLS tstream under the LDAP context and switches active transport from plain to TLS. Failures leave the existing stream unchanged and return `TLDAP_CONNECT_ERROR` or `TLDAP_LOCAL_ERROR`.

## Dependencies and integration points
It depends on `tldap.c` stream accessors, Samba TLS tstream code, TLS parameter peer-name logging, and tevent async request conventions. It is used by StartTLS or LDAPS setup flows.

## Risks and edge cases
Attempting TLS over a GENSEC-wrapped connection is rejected because the code expects the raw plain stream as the TLS base. One path returns an unposted request on missing plain stream, which callers must still handle through normal tevent semantics. Certificate and peer-name validation live in the TLS parameter layer, not here.

## Test signals
Useful coverage includes failed upgrade on disconnected contexts, rejection after GENSEC wrapping, successful stream switch, and propagation of TLS handshake errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap_tls_connect.c -->
