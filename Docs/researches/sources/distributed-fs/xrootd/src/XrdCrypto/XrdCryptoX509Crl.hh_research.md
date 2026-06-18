# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Crl.hh

## Purpose

`XrdCryptoX509Crl.hh` declares the abstract X.509 CRL interface used for revocation checking in certificate-chain validation.

## Important APIs and Types

`XrdCryptoX509Crldata` is an opaque backend pointer. The class exposes validity/expiration, opaque access, dumping, parent file, update times, issuer name/hash, serial-number revocation checks by integer or string, and signature verification against a certificate.

## Control Flow

Chain verification supplies a CRL to generic or GSI verification, which calls `IsRevoked()` for certificates under examination.

## State and Persistence Behavior

No base state is stored. Concrete implementations manage parsed CRL data and backend resources.

## Dependencies and Integration Points

It depends on `XrdCryptoX509.hh`. Factories construct CRL instances from files or CA certificates.

## Risks and Edge Cases

Implementations must define serial-number string formats consistently with certificate `SerialNumberString()`. Expired CRLs must be rejected by callers or `IsValid()`.

## Test Signals

Tests should cover CRL validity intervals, revoked/non-revoked serials, issuer matching, and signature verification.
