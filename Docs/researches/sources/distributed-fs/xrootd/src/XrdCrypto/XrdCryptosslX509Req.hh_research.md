<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Req.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Req.hh

## Purpose
Declares `XrdCryptosslX509Req`, the OpenSSL implementation of `XrdCryptoX509Req` for certificate signing requests.

## Important APIs, types, and functions
- Constructors support serialized buckets and existing `X509_REQ *`.
- Public methods expose opaque CSR pointer, public key wrapper, bucket export, subject, subject hash, extension lookup, and signature verification.
- Private state stores `X509_REQ *creq`, cached subject/hash strings, cached bucket, and `XrdCryptoRSA *pki`.

## Control flow
The header defines a CSR lifecycle of import/adoption, metadata lookup, optional extension access, export, and signature verification.

## State and persistence behavior
Objects own an OpenSSL CSR and RSA wrapper and may cache an export bucket. `Opaque()` exposes raw CSR state to proxy signing helpers and other OpenSSL code.

## Dependencies and integration points
Includes `XrdCryptoX509Req.hh`, OpenSSL X509v3, and BIO headers. It integrates with the factory and proxy creation/signing helpers.

## Risks and edge cases
Raw pointer ownership is central: adopted `X509_REQ *` is freed by this object, and callers using `Opaque()` must not mutate/free it unexpectedly. Cached bucket lifetime is not explicit in the API.

## Test signals
Compile and runtime tests should cover generic base pointer use, ownership of adopted requests, bucket export/import idempotence, and `PKI()` status for public-only request keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Req.hh -->
