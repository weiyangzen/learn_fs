# sources/user-network-fs/samba/source4/lib/tls/wscript_build

## Purpose

This waf script defines the `LIBTLS` subsystem for source4 TLS, certificate generation, TLS tstream wrapping, and optional QUIC-related integration.

## Important APIs, Types, and Functions

It builds `tlscert.c` and `tls_tstream.c` into `LIBTLS` and declares public dependencies: `talloc`, `gnutls`, `GNUTLS_HELPERS`, `samba-hostconfig`, `LIBTSOCKET`, `tevent`, `tevent-util`, `quic`, `libngtcp2`, and `libngtcp2_crypto_gnutls`.

## Control Flow

At build time, waf uses this dependency graph to expose TLS symbols to consumers. Conditional C compilation still controls whether kernel QUIC and ngtcp2 code is active.

## State and Persistence Behavior

No runtime state exists in the build script. It persists only in build metadata.

## Dependencies and Integration Points

The dependency list makes TLS a central integration point between GnuTLS, Samba host configuration, tsocket/tstream infrastructure, tevent, and optional QUIC libraries.

## Risks and Edge Cases

Optional library availability must match the feature macros used in `tls_tstream.c`. Dependency churn can affect many consumers because `LIBTLS` is pulled by `LIBPACKET` and transport code.

## Test Signals

Clean builds with default options and feature-enabled QUIC/ngtcp2 builds are the main signals. Link tests should confirm consumers resolve TLS and optional QUIC symbols correctly.
