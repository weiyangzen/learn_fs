# sources/user-network-fs/samba/source4/lib/tls/tls.h

## Purpose

`tls.h` declares Samba source4 TLS support: certificate autogeneration, TLS parameter construction, asynchronous TLS stream wrapping, synchronous TLS I/O, certificate verification modes, channel bindings, QUIC handshakes, and ngtcp2-backed QUIC stream connection.

## Important APIs, Types, and Functions

The main public types are opaque `struct tstream_tls_params` and `struct tstream_tls_sync`, plus `enum tls_verify_peer_state`. APIs include `tls_cert_generate()`, `tls_verify_peer_string()`, client/server parameter constructors and loadparm wrappers, `tstream_tls_params_quic_prepare()`, enabled/verify/peer-name accessors, `tstream_tls_channel_bindings()`, async TLS connect/accept send/recv functions, sync read/write/pending/setup/channel-binding functions, QUIC handshake functions, and ngtcp2 connect send/recv functions.

## Control Flow

The header defines the public setup sequence: create TLS params from explicit values or loadparm, optionally prepare QUIC, wrap an existing `tstream_context` asynchronously as client/server or set up sync callbacks, then use returned streams through generic tstream operations.

## State and Persistence Behavior

TLS parameters hold certificate credentials, DH params, priority strings, verification policy, peer name, and QUIC enablement internally. Channel bindings become available only after a successful handshake.

## Dependencies and Integration Points

It includes `lib/socket/socket.h`, forward-declares loadparm and tstream types, and exposes APIs consumed by LDAP/SMB transports and QUIC paths. Implementations depend on GnuTLS, tevent, tsocket, loadparm, optional kernel QUIC, and optional ngtcp2.

## Risks and Edge Cases

Verification mode semantics are security-sensitive. `TLS_VERIFY_PEER_CA_AND_NAME` and stricter require a usable peer name. QUIC preparation is conditional and may disable itself for IP peer names. Callers must not assume channel bindings exist before handshake success.

## Test Signals

Compile coverage with and without optional QUIC/ngtcp2 libraries is important. Runtime tests should cover every verify-peer mode, missing CA/CRL/peer-name failures, client/server stream handshakes, sync setup, and QUIC feature gating.
