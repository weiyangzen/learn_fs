# sources/user-network-fs/samba/source4/ldap_server/ldap_server.h

## Purpose

`ldap_server.h` defines the shared state structures and constants for Samba's LDAP server implementation. It is the contract between transport, backend, bind, and extended-operation files.

## Important APIs, Types, and Functions

Key declarations are `enum ldap_server_referral_scheme`, `struct ldapsrv_connection`, `struct ldapsrv_call`, nested `struct ldapsrv_reply`, and `struct ldapsrv_service`. It defines `LDAP_SERVER_MAX_REPLY_SIZE` as 256 MiB and `LDAP_SERVER_MAX_CHUNK_SIZE` as 25 MiB, and includes generated `ldap_server/proto.h`.

## Control Flow

The header has no runtime flow, but its callback fields drive control flow: call wait hooks for async bind/unbind and postprocess hooks for StartTLS/SASL stream changes.

## State and Persistence Behavior

`ldapsrv_connection` owns per-client streams, GENSEC, session, LDB handle, credentials, auth flags, referral scheme, limits, active call, deferred expiry disconnect, and pending calls. `ldapsrv_call` owns one decoded request, replies, output iovecs, wait/postprocess hooks, and notification state. `ldapsrv_service` owns process/service-wide state.

## Dependencies and Integration Points

It depends on LDAP protocol, socket/packet/network, and loadparm types. It is included by all LDAP server implementation files and defines their shared ABI.

## Risks and Edge Cases

The structures are lifetime-sensitive because calls hold private callback state while connections own streams and backend handles. Reply and chunk constants affect memory pressure and client-visible limits.

## Test Signals

Compile/link coverage catches structural drift. Runtime tests should exercise simple bind wait, unbind wait, StartTLS postprocess, SASL postprocess, notification calls, multi-reply writes, and termination with layered streams.
