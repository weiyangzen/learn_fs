# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoBasic.hh

## Purpose

`XrdCryptoBasic.hh` declares the base buffer abstraction shared by crypto facade classes. It stores an optional type label and a mutable binary buffer.

## Important APIs and Types

Public getters include `AsBucket()`, `AsHexString()`, `Length()`, `Buffer()`, and `Type()`. Setters include `FromHex()`, `SetLength()`, `SetBuffer()`, `SetType()`, and `UseBuffer()`. The class owns `lenbuf`, `membuf`, and `type`.

## Control Flow

Derived classes use this as a common serialization and buffer-management layer. `UseBuffer()` bypasses allocation to install caller-provided memory directly.

## State and Persistence Behavior

Instance state is heap-owned and released by the virtual destructor. `Length()` returns a `kXR_int32` value as `int`, so consumers treat buffer lengths as signed 32-bit quantities.

## Dependencies and Integration Points

It depends on XRootD protocol integer types and `XrdSutBucket`. `XrdCryptoCipher` and `XrdCryptoMsgDigest` inherit from it.

## Risks and Edge Cases

The ownership contract for `UseBuffer()` is dangerous because the input is typed as `const char *` but becomes owned mutable storage. The class does not define copy/move constructors, so default copying would double-free pointers if used.

## Test Signals

Compile and runtime tests should prevent accidental value copying and validate bucket/hex conversion behavior.
