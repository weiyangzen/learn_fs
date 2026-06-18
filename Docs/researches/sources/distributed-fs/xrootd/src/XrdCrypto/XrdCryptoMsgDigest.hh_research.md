# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoMsgDigest.hh

## Purpose

`XrdCryptoMsgDigest.hh` declares the abstract interface for message digest implementations in the crypto plugin architecture.

## Important APIs and Types

The class inherits `XrdCryptoBasic` and declares `IsValid()`, `Reset(const char *)`, `Update(const char *, int)`, `Final()`, and `operator==`.

## Control Flow

Consumers reset a digest to a named algorithm, feed data with `Update()`, finalize into the inherited buffer, and compare or inspect the result.

## State and Persistence Behavior

Base state is inherited buffer/type storage; concrete implementations add hash context and validity state.

## Dependencies and Integration Points

It depends on `XrdCryptoBasic.hh` and is constructed through `XrdCryptoFactory::MsgDigest()`.

## Risks and Edge Cases

The equality operator's by-value parameter is unsafe for a raw-pointer-owning hierarchy and can cause accidental copies. Implementations must specify whether `Reset()` can be called after `Final()`.

## Test Signals

Tests should verify common digest algorithms, reset/update/final sequencing, and object-copy prevention or safe semantics.
