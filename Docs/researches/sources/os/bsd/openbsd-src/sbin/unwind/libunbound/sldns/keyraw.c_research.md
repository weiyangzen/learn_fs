# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/keyraw.c

`keyraw.c` implements raw DNSSEC key helpers over DNSKEY wire-format RDATA. It computes DNSKEY public-key sizes for DSA, RSA, GOST, ECDSA, Ed25519, and Ed448 algorithms when compiled in, and implements the DNSSEC key-tag calculation including the RSAMD5 legacy special case.

When OpenSSL support is enabled, the file converts raw DNSKEY public key material into OpenSSL key objects. RSA and DSA parsing extracts BIGNUM components from DNS wire layout, then builds either legacy RSA/DSA objects or OpenSSL 3 `EVP_PKEY` objects through `OSSL_PARAM_BLD`. ECDSA handling chooses the P-256/P-384 group and prepends the uncompressed-point marker before importing. GOST, Ed25519, and Ed448 use fixed ASN.1 public-key prefixes around the raw DNSKEY bytes.

The optional GOST path manages an OpenSSL engine reference with `sldns_key_EVP_load_gost_id()` and `sldns_key_EVP_unload_gost()`. The file is heavily feature-macro gated, so supported algorithms depend on compile-time crypto options and OpenSSL/LibreSSL API availability.

Most functions are defensive about minimum lengths and expected encoded key sizes. Ownership is important: conversion helpers free partially built BIGNUM/OpenSSL state on errors, and successful legacy `EVP_PKEY_assign_*` paths transfer ownership into the returned `EVP_PKEY`.

The file also provides `sldns_digest_evp()`, a small wrapper around OpenSSL EVP digest initialization, update, and finalization.
