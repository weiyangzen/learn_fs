# sources/user-network-fs/samba/source4/ldap_server/ldap_extended.c

## Purpose

`ldap_extended.c` implements Samba LDAP ExtendedRequest operations: StartTLS and WhoAmI. It queues extended responses and, for StartTLS, defers the TLS handshake until after the success response is sent.

## Important APIs, Types, and Functions

The exported entry point is `ldapsrv_ExtendedRequest()`. Operations are listed in `extended_ops[]` as `struct ldapsrv_extended_operation`. Internal handlers are `ldapsrv_StartTLS()`, `ldapsrv_whoami()`, and StartTLS postprocess send/recv/done functions.

## Control Flow

`ldapsrv_ExtendedRequest()` initializes an `ExtendedResponse`, finds a matching OID, and lets the operation queue success or return an LDAP-coded error. StartTLS rejects existing TLS, existing SASL wrapping, and pending calls; on success it queues `LDAP_SUCCESS` and installs a postprocess hook that runs `tstream_tls_accept_send()` and switches `conn->sockets.active` to TLS. WhoAmI returns `u:DOMAIN\account` for non-anonymous sessions and no value for anonymous sessions.

## State and Persistence Behavior

StartTLS creates `conn->sockets.tls` and changes the active stream after response write completion. WhoAmI only reads session state. Unsupported operations only queue responses.

## Dependencies and Integration Points

It depends on LDAP server postprocess hooks, tstream TLS parameters, service stream state, generated auth NDR types, and security token helpers. It is compiled into `service_ldap` with the transport, backend, and bind files.

## Risks and Edge Cases

Ordering is critical: stream switching must happen only after the StartTLS response is written. StartTLS during in-progress SASL bind is noted as TODO. WhoAmI assumes non-anonymous session info has user info.

## Test Signals

Tests should cover StartTLS success, already-TLS error, SASL-wrapped error, pending-call `LDAP_BUSY`, failed TLS accept, anonymous and authenticated WhoAmI, and unsupported OID diagnostics.
