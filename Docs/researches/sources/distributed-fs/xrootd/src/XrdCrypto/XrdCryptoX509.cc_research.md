# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509.cc

## Purpose

`XrdCryptoX509.cc` implements common abstract X.509 certificate behavior: type names, generic validity checks, diagnostic dumping, hostname wildcard matching, and default stubs for implementation-specific operations.

## Important APIs and Functions

`Dump()` prints certificate file, type, serial, subject/issuer names and hashes, validity interval, and PKI status. `IsValid(int when)` checks current or supplied time against `NotBefore() - 600 seconds` and `NotAfter()`. `IsExpired()` checks only `NotAfter()`. Most accessors (`BitStrength`, time/name/hash/key/extension/export/verify methods) are abstract stubs. `MatchHostnames()` lowercases pattern and hostname, supports wildcard matching in the first DNS label, and requires remaining labels to match exactly.

## Control Flow

Generic validity delegates certificate-specific times to concrete subclasses. Dumping calls multiple virtual methods and formats local-time strings. Hostname matching first checks exact equality, then tokenizes the first label and applies `XrdOucString::matches()` to that label only.

## State and Persistence Behavior

The base stores `type` only. It uses static type-name strings and a fixed allowed clock skew of 600 seconds.

## Dependencies and Integration Points

It depends on `XrdCryptoX509.hh`, `XrdCryptoTrace.hh`, `XrdCryptoRSA`, `XrdSutBucket`, and `XrdOucString`. Concrete OpenSSL implementations provide the cryptographic data.

## Risks and Edge Cases

`Dump()` assumes validity times can be converted and that `asctime_r` output is nonempty before trimming the trailing newline. `MatchHostnames()` allows patterns such as `F*.com`, which may be broader than modern certificate hostname rules. Abstract stubs return failure values that can mask missing overrides until runtime.

## Test Signals

Tests should cover validity skew, expired/not-yet-valid certs, wildcard SAN hostname matching, exact case-insensitive matches, and concrete override completeness.
