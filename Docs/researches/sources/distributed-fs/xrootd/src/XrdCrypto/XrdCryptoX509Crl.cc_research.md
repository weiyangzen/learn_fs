# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Crl.cc

## Purpose

`XrdCryptoX509Crl.cc` provides abstract default behavior for X.509 certificate revocation lists.

## Important APIs and Functions

Most methods (`Dump`, `IsValid`, update time accessors, parent file, issuer/hash, opaque access, signature verification, and serial revocation checks) are abstract stubs. `IsExpired(int when)` is implemented generically by comparing the current or supplied time with `NextUpdate()`.

## Control Flow

Concrete CRL implementations supply parsing, validity, issuer, and revocation behavior. Generic expiration is a simple time comparison.

## State and Persistence Behavior

The base class stores no state. Concrete subclasses own backend CRL handles.

## Dependencies and Integration Points

It depends on `XrdCryptoX509Crl.hh` and `XrdCryptoX509`. Chain verification can pass a CRL to reject revoked certificates.

## Risks and Edge Cases

The default `IsRevoked()` stubs return true, a fail-closed behavior if a concrete override is missing. `IsExpired()` depends on `NextUpdate()` returning a valid epoch value; the abstract default returns `-1`, making the base appear expired.

## Test Signals

Tests should verify concrete CRL parsing, expiration, issuer signature verification, serial-number string/int revocation checks, and fail-closed behavior when revocation cannot be determined.
