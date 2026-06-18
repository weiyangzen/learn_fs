# sources/storage-engines/foundationdb/flow/MkCert.cpp

## Purpose
Implements test TLS certificate/key generation, PEM read/write/printing, certificate-chain construction, default certificate specs, and password-protected private-key output.

## Important APIs, Types, And Functions
`traceAndThrow()` and `OSSL_ASSERT` convert OpenSSL failures to traced `tls_error()`. `CertAndKeyNative` bridges native `X509`/`PrivateKey` to `CertAndKeyRef` PEM. `readX509CertPem()`, `writeX509CertPem()`, `printCert()`, and `printPrivateKey()` handle PEM/native conversion. `makeEcP256()` and `makeRsa4096Bit()` generate keys, though certificate creation uses P-256. `makeCertNative()` creates and signs X.509v3 certs. Public helpers include `CertAndKeyRef::make()`, `CertSpecRef::make()`, `concatCertChain()`, `makeCertChain()`, `makeCertChainSpec()`, `CertKind::getCommonName()`, and `makePasswCert()`.

## Control Flow
Certificate creation builds a new P-256 keypair, allocates X509, sets version/serial/validity/pubkey/subject/issuer, constructs configured extensions through `X509V3_EXT_nconf_nid`, signs with either self key or issuer key, and returns PEM. Chain creation either self-signs the last spec as root and walks backward to leaf, or deep-copies a supplied root and signs intermediates/leaves from it.

## State And Persistence Behavior
Generated cert/key bytes are arena-backed `StringRef`/`VectorRef` values. Random serials use deterministic random. OpenSSL error state may be consumed for tracing. No files are written here; CLI code writes outputs.

## Dependencies And Integration Points
Depends on Flow Arena/StringRef, `PrivateKey`, Trace, ScopeExit, deterministic random, and OpenSSL/BoringSSL X509/EVP APIs. Used by TLS tests and `MkCertCli.cpp`.

## Risks And Edge Cases
This is test infrastructure, not production CA management. Serial range is limited to `1e10`, validity defaults to one year, and subject values are fixed testing labels. Extension names/values must be OpenSSL-recognized and null-terminable after conversion. Failure handling traces and throws but depends on OpenSSL error availability.

## Test Signals
No local unit test. Signals come from TLS tests that consume generated chains, CLI success, OpenSSL parse/print behavior, and failed `OSSL_ASSERT` TraceEvents.
