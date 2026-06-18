# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptogsiX509Chain.hh

## Purpose

`XrdCryptogsiX509Chain.hh` declares the GSI policy-enforcing subclass of `XrdCryptoX509Chain`.

## Important APIs and Types

`kOptsRfc3820` enables required proxy-certificate extension validation. `XrdCryptogsiX509Chain` constructors accept an optional initial certificate or chain plus an optional `XrdCryptoFactory *`. The class overrides `Verify()` and keeps `SubjectOK()` private for proxy naming rules.

## Control Flow

Users build or copy a chain, provide a factory capable of proxy extension parsing, and call `Verify()` with GSI options. The subclass delegates generic cryptographic checks to the base and adds GSI sequencing/proxy checks.

## State and Persistence Behavior

The only new state is the non-owning `cfact` pointer. All list and cache state is inherited from `XrdCryptoX509Chain`.

## Dependencies and Integration Points

It depends on `XrdCryptoX509Chain.hh` and forward-declares `XrdCryptoFactory`. It integrates with GSI authentication and OpenSSL plugin proxy hooks.

## Risks and Edge Cases

The factory pointer lifetime must outlive verification calls. Without a proxy-info-capable factory, RFC 3820 checks cannot be performed.

## Test Signals

Tests should instantiate the subclass with null and real factories, verify option handling, and ensure inherited chain ownership rules remain clear.
