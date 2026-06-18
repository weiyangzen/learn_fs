# sources/storage-engines/foundationdb/flow/include/flow/MkCert.h

## Purpose
`MkCert.h` declares test/support helpers for generating private keys, certificate specs, certificate chains, and PEM output for Flow TLS scenarios.

## Important APIs, Types, And Functions
Key APIs are `printCert()`, `printPrivateKey()`, `makeEcP256()`, `makeRsa4096Bit()`, `Asn1EntryRef`, certificate kind tags, `CertKind`, `CertSpecRef::make()`, `CertAndKeyRef::make()`, `concatCertChain()`, `makeCertChainSpec()`, `makeCertChain()`, and `makePasswCert()`.

## Control Flow
Callers build certificate specs from a side/depth or explicit kind, generate or pass a root authority, and produce PEM cert/key pairs. Empty issuer means self-signed. Chain helpers create consistent subject/issuer names for server or client TLS tests.

## State And Persistence Behavior
Certificate and key bytes are stored as `StringRef` values backed by an `Arena`. `deepCopy()` copies PEMs into another arena. Generated PEMs may be written by print helpers but the header itself owns no persistent storage.

## Dependencies And Integration Points
It depends on `Arena`, `Error`, `PKey`, fmt, strings, variants, and OpenSSL-backed implementation code. It integrates with TLS configuration and tests requiring server/client roots, intermediates, leaves, and password-protected keys.

## Risks And Edge Cases
Arena lifetime must outlive `StringRef` users. Certificate validity offsets are relative to creation time, so clock-sensitive tests can be flaky. Chain depth and root authority handling must keep issuer/subject relationships valid.

## Test Signals
Tests should parse generated PEMs, verify chain trust for server and client sides, check root/intermediate/leaf flags, password-protected key behavior, arena deep-copy lifetime, and print helper output.
