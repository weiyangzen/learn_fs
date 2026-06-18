<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslRSA.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslRSA.hh

## Purpose
Declares `XrdCryptosslRSA`, the OpenSSL concrete implementation of the generic RSA interface.

## Important APIs, types, and functions
- Private state includes `EVP_PKEY *fEVP`, `publen`, and `prilen`.
- Constructors cover generated keys, imported public PEM, adopted `EVP_PKEY`, and copy construction.
- `Opaque()` exposes the underlying `EVP_PKEY`.
- Export/import and encryption/decryption methods implement the `XrdCryptoRSA` contract.

## Control flow
The header defines a lifecycle where keys are generated or imported, optionally completed with private material, exported as PEM, and used for RSA operations. `Opaque()` is the bridge used by certificate code and OpenSSL helper code.

## State and persistence behavior
Instances own an OpenSSL key pointer. Export methods expose public and private key material into caller buffers; `Opaque()` exposes internal ownership-sensitive state.

## Dependencies and integration points
Inherits from `XrdCryptoRSA` and includes OpenSSL `evp.h`. It is used by certificates for `PKI()` objects and by the factory for RSA construction.

## Risks and edge cases
The raw `Opaque()` pointer makes ownership conventions critical: some constructors adopt `EVP_PKEY*`, and callers must not double-free. Export length cache invalidation must remain correct after imports.

## Test signals
Compile and runtime tests should verify key ownership with certificate wrappers, status transitions from public to complete, and generic-interface calls through `XrdCryptoRSA *`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslRSA.hh -->
