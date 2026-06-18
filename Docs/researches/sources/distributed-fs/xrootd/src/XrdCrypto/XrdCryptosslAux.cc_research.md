<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslAux.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslAux.cc

## Purpose
Implements OpenSSL utility functions exported through `XrdCryptosslAux.hh`: PBKDF2 key derivation, X.509 certificate and chain verification, PEM bucket/file import/export, TLS peer certificate stack import, ASN.1 time conversion, and OpenSSL `X509_NAME` formatting. This is the glue layer that lets the generic `XrdCrypto` interfaces move OpenSSL objects through XRootD chains, buckets, files, and TLS contexts.

## Important APIs, types, and functions
- Global `sslTrace` is the shared trace sink used by `XrdCryptosslTrace.hh`; `gErrVerifyChain` is a static verification error latch used by chain verification.
- `XrdCryptosslKDFunLen()` returns the default PBKDF2 output length `kSslKDFunDefLen`.
- `XrdCryptosslKDFun()` derives keys with `PKCS5_PBKDF2_HMAC_SHA1`, defaulting to 10,000 iterations and allowing a salt prefix of the form `$$<iterations>$<salt>`.
- `XrdCryptosslX509VerifyCert()` verifies one certificate with another certificate's public key through `X509_verify`.
- `XrdCryptosslX509VerifyChain()` builds an `X509_STORE`, inserts the chain's CA certificate, builds a STACK for the rest, and calls `X509_verify_cert`.
- `XrdCryptosslX509ExportChain()`, `XrdCryptosslX509ToFile()`, and `XrdCryptosslX509ChainToFile()` serialize certificates and optional private keys to an `XrdSutBucket` or PEM file.
- `XrdCryptosslX509ParseFile()`, `XrdCryptosslX509ParseBucket()`, and `XrdCryptosslX509ParseStack()` ingest PEM files, serialized buckets, or `XrdTlsPeerCerts` into an `XrdCryptoX509Chain`.
- `XrdCryptosslASN1toUTC()` converts OpenSSL `ASN1_TIME` UTCTime or GeneralizedTime to epoch seconds.
- `XrdCryptosslNameOneLine()` converts an `X509_NAME` into XRootD's slash-delimited name string.

## Control flow
Key derivation first normalizes the output length, then scans the salt for an iteration override before calling OpenSSL PBKDF2. Chain verification expects a chain with a CA first, inserts that CA into a newly allocated store, pushes remaining certs into a stack, initializes an `X509_STORE_CTX` with the first non-CA cert as target, and verifies. Export paths reorder certificate chains, write the end certificate first, optionally write its private key, then walk issuer-to-subject links until reaching a CA or self-signed certificate. Parse paths read all PEM certificates first, then rewind or open a separate key file to look for a private key and attach it to the matching non-CA certificate by comparing public/private `EVP_PKEY`s. Bucket parsing follows the same two-pass pattern through a memory BIO. TLS stack parsing imports the peer certificate and then the peer chain, manually incrementing OpenSSL refcounts for chain certificates because ownership expectations differ between `SSL_get_peer_chain` and `XrdCryptosslX509`.

## State and persistence behavior
The file does not own durable state except files it writes. `XrdCryptosslX509ChainToFile()` opens the destination with `fopen("w")`, locks the descriptor with `XrdSutFileLocker`, sets permissions to `0600`, and writes proxy-style PEM content. Bucket exports allocate `XrdSutBucket` objects that copy BIO contents via `SetBuf`. Imported OpenSSL objects are handed to `XrdCryptosslX509` wrappers, which then own and later free them. `gErrVerifyChain` is process-global mutable state and is only meaningful around chain verification.

## Dependencies and integration points
Depends on OpenSSL PEM/BIO/X509/EVP APIs, `XrdCryptoX509Chain`, `XrdCryptosslX509`, `XrdCryptosslRSA`, `XrdSutBucket`, `XrdSutFileLocker`, `XrdTlsPeerCerts`, `XrdOucString`, and tracing macros. It is reached directly through `XrdCryptosslFactory` hook accessors and indirectly by certificate, CRL, and request classes for time and name parsing. OpenSSL 3 compatibility appears in public-key comparison via `EVP_PKEY_eq`; older versions use `EVP_PKEY_cmp`.

## Risks and edge cases
Several error paths return without freeing all intermediate OpenSSL allocations, especially in early returns after store/stack/context setup; leak tests should cover failures. `XrdCryptosslX509VerifyCB()` appears inverted: it sets `gErrVerifyChain = 1` when `ok != 0`, and `XrdCryptosslX509VerifyChain()` installs a null callback rather than this function, so reported error codes may be weak. `XrdCryptosslKDFun()` assumes `salt` and `slen` are valid before `memchr(salt+1, ...)`. `XrdCryptosslX509ExportChain()` dereferences `c->PKI()` when `withprivatekey` is true without checking `k`. `XrdCryptosslX509ParseFile(FILE*,...)` calls `fclose(fcer)` on one allocation-failure path even though the caller is documented as owning the FILE. `XrdCryptosslASN1toUTC()` parses raw ASN.1 data and adjusts via `XrdCryptoTZCorr`; date/timezone boundary tests are important.

## Test signals
Useful tests include PBKDF2 known vectors with default and salt-encoded iteration counts; certificate chain verification for valid, wrong issuer, missing CA, and out-of-order chains; PEM chain export/import with and without private key; file output permission and locking behavior; bucket round trips; TLS peer stack refcount ownership under ASAN; ASN.1 UTCTime and GeneralizedTime conversion around 1950/2050 boundaries; and OpenSSL 1.1/3.x key comparison behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslAux.cc -->
