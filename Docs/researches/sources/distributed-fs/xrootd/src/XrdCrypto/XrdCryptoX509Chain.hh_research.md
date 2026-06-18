# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Chain.hh

## Purpose

`XrdCryptoX509Chain.hh` declares the certificate-chain container and generic verification API used by XRootD crypto code.

## Important APIs and Types

`x509ChainVerifyOpt_t` carries option bits, verification time, max path length, and optional CRL. Option bits include `kOptsCheckSelfSigned` and `kOptsCheckSubCA`. `XrdCryptoX509ChainNode` stores one certificate pointer and next node. `XrdCryptoX509Chain` exposes CA status, error codes, dump/accessors, list modifiers, CA checking, cleanup, subject/issuer search, validity checking, reordering, verification, and pseudo-iterator methods.

## Control Flow

Users build a chain, optionally reorder/check validity, and call `Verify()` with options. Iterator methods use internal state instead of external iterator objects.

## State and Persistence Behavior

Protected members store linked-list pointers, iterator state, effective CA, size, last error, cached names/hashes, and CA status. Node destructors do not delete certificates; cleanup semantics are explicit.

## Dependencies and Integration Points

It depends on `XrdSutBucket`, `XrdCryptoX509`, and `XrdCryptoX509Crl`. It is the base for GSI-specific validation and uses concrete certificate implementations provided by crypto plugins.

## Risks and Edge Cases

Ownership is ambiguous: destructor deletes nodes only, while `Cleanup()` can delete certificate contents. Copy construction shares certificate pointers. The internal iterator is not reentrant.

## Test Signals

Tests should validate ownership expectations, iterator behavior, error-code mapping, and verification options.
