<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509.hh

## Purpose
Declares `XrdCryptosslX509`, the OpenSSL concrete implementation of `XrdCryptoX509`.

## Important APIs, types, and functions
- Constructors support loading from certificate/key paths, serialized buckets, and existing `X509 *`.
- Public methods expose opaque OpenSSL data, extension dumping, PKI access/mutation, bucket export, source file, proxy type, bit strength, serials, validity, subject/issuer names and hashes, SAN matching, extension lookup, and signature verification.
- Private members store `X509 *cert`, cached validity/name/hash/source/bucket/key/proxy state, ASN.1 dump helpers, and static proxy type names.

## Control flow
The header defines the full certificate wrapper contract used by the factory, chain helpers, CRL helpers, and proxy code. The implementation lazily fills most metadata through the public getters.

## State and persistence behavior
Objects own an OpenSSL certificate and RSA wrapper, cache computed metadata, and may cache an exported bucket. `Opaque()` exposes the raw `X509 *` for OpenSSL calls elsewhere.

## Dependencies and integration points
Includes `XrdCryptoX509.hh` plus OpenSSL X509v3/BIO/EVP headers. It is the central OpenSSL certificate type used by chain parsing, verification, CRL verification, and proxy helper code.

## Risks and edge cases
Raw opaque pointer access and constructor adoption of `X509 *` require exact ownership discipline. Cached strings can become stale only if the underlying cert were mutated through `Opaque()`, which the interface permits. `PKI()` exposes mutable key wrapper state.

## Test signals
Compile tests should verify base-class polymorphism and OpenSSL type availability. Runtime tests should cover each constructor, `Opaque()` interop with OpenSSL verification, lazy getter idempotence, and ownership on copied/up-refed certificates from TLS stacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509.hh -->
