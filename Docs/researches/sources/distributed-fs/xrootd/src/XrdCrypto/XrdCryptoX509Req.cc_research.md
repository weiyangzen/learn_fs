# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Req.cc

## Purpose

`XrdCryptoX509Req.cc` implements shared behavior and abstract defaults for X.509 certificate-signing requests.

## Important APIs and Functions

`Dump()` prints subject, subject hash, and PKI status through trace macros. `IsValid()`, `Subject()`, `SubjectHash()`, `Opaque()`, `PKI()`, `GetExtension()`, `Export()`, and `Verify()` are abstract stubs returning failure or null defaults.

## Control Flow

Concrete request implementations supply parsing, export, key retrieval, extension lookup, and signature verification. Dumping delegates to those virtual methods and handles missing PKI.

## State and Persistence Behavior

The base class stores a plugin/request `version` value via the header constructor. Concrete subclasses own backend request data.

## Dependencies and Integration Points

It depends on `XrdCryptoX509Req.hh` and `XrdCryptoTrace.hh`. Proxy creation hooks in `XrdCryptoFactory` create and sign request objects.

## Risks and Edge Cases

`Dump()` assumes `Subject()` and `SubjectHash()` are safe to stream even if concrete methods return null. Missing overrides fail only at runtime via diagnostics.

## Test Signals

Tests should cover concrete request validity, subject/hash extraction, export/import bucket behavior, version propagation, and signature verification.
