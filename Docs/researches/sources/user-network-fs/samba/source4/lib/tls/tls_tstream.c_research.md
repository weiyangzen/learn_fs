# sources/user-network-fs/samba/source4/lib/tls/tls_tstream.c

## Purpose

`tls_tstream.c` implements TLS and QUIC transport wrappers for Samba tstreams. It builds GnuTLS client/server parameters, verifies peers, exposes TLS channel bindings, wraps existing tstreams with asynchronous encrypted read/write/disconnect operations, supports synchronous callback-based TLS, optionally drives kernel QUIC handshakes, and optionally implements an ngtcp2 client stream over an existing connected UDP socket.

## Important APIs, Types, and Functions

Public functions include `tls_verify_peer_string()`, TLS parameter constructors/accessors, `tstream_tls_channel_bindings()`, `_tstream_tls_connect_send()`, `tstream_tls_connect_recv()`, `_tstream_tls_accept_send()`, `tstream_tls_accept_recv()`, sync TLS APIs, `tstream_tls_quic_handshake_send/recv()`, `tstream_tls_quic_handshake()`, `_tstream_tls_ngtcp2_connect_send()`, and `tstream_tls_ngtcp2_connect_recv()`. Key internal state types are `struct tstream_tls`, `struct tstream_tls_params_internal`, `struct tstream_tls_sync`, and, under `HAVE_LIBNGTCP2`, `struct tstream_ngtcp2` plus queued buffer structures.

## Control Flow

TLS parameter construction loads trust roots, CRLs, priority strings, peer names, server cert/key files, and DH parameters. `tstream_tls_prepare_gnutls()` initializes a GnuTLS session, applies priorities and credentials, sets SNI when appropriate, and configures server certificate requests. Async connect/accept create a `tstream_context`, install GnuTLS pull/push callbacks that delegate to the plain stream, and drive `gnutls_handshake()` through tevent retries. Read/write copy iovecs into fixed buffers and call GnuTLS record functions until complete or blocked. QUIC paths either use kernel handshake steps or ngtcp2 callbacks and timers to drive handshake, datagram I/O, stream read/write queues, monitoring, and disconnect.

## State and Persistence Behavior

TLS stream state persists the plain stream, current error, GnuTLS session, role, verification policy, peer name, channel bindings, current tevent context, pending push/pull subrequests, and active management/read/write/disconnect requests. TLS params hold long-lived credentials referenced by sessions. ngtcp2 state persists connection IDs, path addresses, buffers, timers, keepalive settings, and request pointers. Server parameter setup may trigger certificate autogeneration through `tlscert.c`.

## Dependencies and Integration Points

The implementation depends on GnuTLS, Samba GnuTLS helpers, tevent, tsocket internals, tdgram, loadparm, file utilities, time utilities, optional kernel QUIC, optional ngtcp2 and `ngtcp2_crypto_gnutls`, and Samba debug/NTSTATUS helpers. It integrates with generic tstream users and TLS configuration from `loadparm_context`.

## Risks and Edge Cases

This file is concurrency- and state-machine-heavy. Errors are latched and can complete outstanding requests later. The async GnuTLS pull/push callbacks must map `EAGAIN` exactly or handshakes/read/write can stall. Verification policy around IP peer names, missing CRLs, and strict mode is security-sensitive. Server key permissions are enforced because of CVE-2013-4476. QUIC support is compile-time conditional.

## Test Signals

High-value tests include client and server TLS handshakes with valid, expired, revoked, wrong-name, IP-name, missing-CA, and missing-CRL certificates; channel-binding validation; simultaneous read/write during handshake and shutdown; sync callback I/O with EINTR/EAGAIN; loadparm-driven configuration; kernel QUIC handshake success/failure when available; and ngtcp2 stream read/write/disconnect under packet loss, blocked congestion window, timeout, and peer reset.
