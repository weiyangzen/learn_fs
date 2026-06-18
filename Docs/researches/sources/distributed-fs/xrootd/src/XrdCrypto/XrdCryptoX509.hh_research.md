# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509.hh

## Purpose

`XrdCryptoX509.hh` declares the abstract representation of one X.509 certificate in the XRootD crypto layer.

## Important APIs and Types

`EX509Type` distinguishes CA, end-entity certificate, proxy, and unknown. The interface exposes validity/expiration, opaque backend access, RSA key access, export, dump/extension dump, parent file, proxy type, bit strength, serial number, validity interval, issuer/subject names and hashes, SAN hostname matching, extension lookup, signature verification, and static hostname matching.

## Control Flow

Consumers and chain validators call generic base methods where possible and rely on concrete plugin overrides for backend-specific certificate parsing and cryptographic verification.

## State and Persistence Behavior

The base stores only the certificate type. Concrete implementations manage certificate handles and associated key objects.

## Dependencies and Integration Points

It depends on XRootD protocol integer types, `XrdSutBucket`, and `XrdCryptoRSA`. `XrdCryptoX509Chain`, CRLs, requests, and factories all depend on this interface.

## Risks and Edge Cases

The abstract interface exposes many borrowed `const char *` values whose lifetime depends on concrete implementations. `MatchesSAN()` is pure virtual, so all concrete cert classes must implement SAN parsing correctly for TLS hostname verification.

## Test Signals

Tests should validate concrete certificate parsing, SAN matching, serial string handling, extension lookup, export/import, and signature verification.
