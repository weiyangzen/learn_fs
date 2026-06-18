# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/keyraw.h

`keyraw.h` declares the raw DNSSEC key API. The non-OpenSSL surface covers DNSKEY public-key size calculation and DNSSEC key-tag calculation directly from uncompressed wire-format RDATA.

When SSL support is compiled in, the header exposes OpenSSL conversion helpers for DSA, RSA, GOST, ECDSA, Ed25519, and Ed448 public keys, plus the generic EVP digest wrapper. Legacy RSA/DSA object-returning functions are hidden when the OpenSSL 3 parameter-builder path is available.

The header is the narrow contract between DNS wire/RDATA parsing and crypto verification code: callers provide raw DNSKEY bytes and receive OpenSSL public-key objects or simple DNSSEC metadata values.
