# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoMsgDigest.cc

## Purpose

`XrdCryptoMsgDigest.cc` provides the abstract message-digest base implementation and equality comparison for digest buffers.

## Important APIs and Functions

`IsValid()`, `Reset()`, `Update()`, and `Final()` are abstract stubs that log diagnostics and return failure defaults. `operator==` compares two digest objects by length and byte content using inherited `Length()` and `Buffer()`.

## Control Flow

Concrete digest implementations perform actual digest lifecycle operations. The base equality method succeeds only when lengths match and `memcmp()` over the digest buffer is zero.

## State and Persistence Behavior

Digest bytes and type state are inherited from `XrdCryptoBasic`; concrete implementations may maintain additional hash context.

## Dependencies and Integration Points

It depends on `XrdCryptoAux.hh` and `XrdCryptoMsgDigest.hh`. Factories construct concrete digest implementations for protocol/authentication code.

## Risks and Edge Cases

`operator==` takes its parameter by value, but `XrdCryptoMsgDigest` inherits raw owning pointers and lacks a safe copy constructor; passing by value can trigger shallow-copy double-free or other lifetime bugs if the default copy is used. The comparison is not constant-time.

## Test Signals

Tests should avoid value-copy hazards by changing/covering the operator contract, compare equal and unequal digest buffers, and verify concrete digest lifecycle behavior.
