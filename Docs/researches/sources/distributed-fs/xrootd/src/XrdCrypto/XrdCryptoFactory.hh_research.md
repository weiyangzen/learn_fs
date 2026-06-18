# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoFactory.hh

## Purpose

`XrdCryptoFactory.hh` declares the central abstract factory and function-pointer hook types that decouple XRootD crypto consumers from concrete implementations such as OpenSSL.

## Important APIs and Types

The file defines KDF hook types, X.509 certificate/chain parsing and verification hook types, proxy certificate OIDs and proxy hook types, `XrdProxyOpt_t`, and the `XrdCryptoFactory` class. The factory constructs ciphers, message digests, RSA keys, X.509 certs, CRLs, and requests, and returns implementation-specific hooks for chain parsing/export/proxy operations.

## Control Flow

Consumers call `GetCryptoFactory()` to load a named implementation, then use virtual constructors and hook accessors. Concrete factories override base methods; base methods are abstract diagnostics.

## State and Persistence Behavior

Factory instances expose a fixed-length name and integer ID. Static loader/cache state is hidden in the `.cc` file.

## Dependencies and Integration Points

It depends on `XrdCryptoAux.hh` plus forward declarations for XRootD crypto classes, `XrdOucString`, and TLS peer cert wrappers. It defines the ABI that concrete crypto plugins must satisfy.

## Risks and Edge Cases

Function-pointer hooks make null checks essential: some implementations may not support optional features such as VOMS or proxy creation. `MAXFACTORYNAMELEN` constrains names but callers can pass longer names unless the implementation validates them.

## Test Signals

ABI tests should compile a minimal factory plugin and verify every required symbol and hook type matches. Runtime tests should exercise optional hook absence.
