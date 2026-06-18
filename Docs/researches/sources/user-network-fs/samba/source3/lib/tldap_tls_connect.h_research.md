<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap_tls_connect.h -->
# sources/user-network-fs/samba/source3/lib/tldap_tls_connect.h

## Purpose
This header declares the TLS upgrade API for tldap connections.

## Important APIs, types, and functions
It forward declares `tevent_context`, `tldap_context`, `loadparm_context`, and `tstream_tls_params`, then exposes async `tldap_tls_connect_send`, receive `tldap_tls_connect_recv`, and synchronous `tldap_tls_connect`.

## Control flow
Callers supply an existing tldap context and prepared TLS parameters. Async callers wait for recv; sync callers use the wrapper.

## State and persistence behavior
The header has no state. Implementations may replace the active LDAP stream with a TLS stream on success.

## Dependencies and integration points
It is included by LDAP connection setup code that performs StartTLS or TLS-first LDAP transport creation.

## Risks and edge cases
Consumers must build correct `tstream_tls_params`, including peer name and trust settings, because this API only transports them.

## Test signals
Compile coverage verifies signatures; transport integration tests should validate TLS negotiation and channel binding availability for subsequent GENSEC bind.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap_tls_connect.h -->
