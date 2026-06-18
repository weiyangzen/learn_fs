# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoRSA.hh

## Purpose

`XrdCryptoRSA.hh` declares the abstract RSA public-key interface used by XRootD crypto plugins.

## Important APIs and Types

`XrdCryptoRSAdata` is an opaque backend pointer. `ERSAStatus` tracks invalid, public-only, and complete key states. The interface exposes opaque access, dumping, output lengths, import/export of public/private keys, string export helpers, raw public/private encrypt/decrypt methods, and bucket wrappers.

## Control Flow

Consumers obtain an RSA object from a factory, import or generate key material, then use raw or bucket APIs depending on protocol serialization needs.

## State and Persistence Behavior

The base stores `status`; concrete implementations own backend key state. Status strings are exposed through `Status()`.

## Dependencies and Integration Points

It depends on `XrdSutBucket`, `XrdOucString`, and `XrdCryptoAux.hh`. X.509 objects expose certificate public keys as `XrdCryptoRSA`.

## Risks and Edge Cases

The class is non-copy-safe by default because concrete subclasses may own opaque resources. The interface uses signed lengths and raw buffers, so callers must respect implementation limits.

## Test Signals

Tests should verify status transitions, export/import round trips, and error behavior for using private operations on public-only keys.
