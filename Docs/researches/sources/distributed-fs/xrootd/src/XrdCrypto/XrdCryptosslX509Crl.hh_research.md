<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Crl.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Crl.hh

## Purpose
Declares `XrdCryptosslX509Crl`, the OpenSSL implementation of `XrdCryptoX509Crl`.

## Important APIs, types, and functions
- Constructors support file path with option, FILE handle, and CA certificate distribution-point discovery.
- Public methods expose validity, opaque CRL pointer, dump/source metadata, update times, issuer names/hashes, revocation checks, signature verification, PEM output, and critical-extension detection.
- Private helpers handle file-type detection, cache loading, file/FILE initialization, and URI initialization.
- Private state stores `X509_CRL *crl`, cached times, issuer strings/hashes, source/URI strings, revoked count, and `XrdSutCache`.

## Control flow
The header defines a CRL lifecycle of construction/loading, metadata access, revocation lookup, optional verification, and optional file output.

## State and persistence behavior
Objects own a CRL and an in-memory cache. URI initialization and `ToFile()` can touch the filesystem through implementation methods. `Opaque()` exposes the raw `X509_CRL *`.

## Dependencies and integration points
Includes OpenSSL X509v3, `XrdSutCache`, and generic `XrdCryptoX509Crl`. It forward-declares `XrdCryptoX509` for CA-based construction and verification.

## Risks and edge cases
Raw `Opaque()` exposes mutable internal CRL state. Cache correctness is central to `IsRevoked()` behavior. The constructor overload with `opt` implies file/URI selection but the enum/meaning is not self-documenting in this header.

## Test signals
Interface tests should cover all constructor overloads, null/invalid CRL behavior for every getter, `Opaque()` interop with OpenSSL, and FILE-based construction without double-closing caller handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Crl.hh -->
