# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoBasic.cc

## Purpose

`XrdCryptoBasic.cc` implements a generic owned byte buffer plus optional type string used as the base for crypto objects such as ciphers and message digests.

## Important APIs and Functions

The constructor copies an optional type string and initializes an optional byte buffer. `AsBucket()` copies the current buffer into an `XrdSutBucket`. `AsHexString()` converts up to `XrdSutMAXBUF / 2 - 1` bytes to a static hex string. `FromHex()` decodes a hex string into a new owned buffer. `SetLength()`, `SetBuffer()`, and `SetType()` mutate the owned fields, while `UseBuffer()` from the header transfers raw pointer ownership without copying.

## Control Flow

Mutation methods allocate new buffers first, copy or zero-fill data, then replace the old buffer. `FromHex()` computes output size, decodes through `XrdSutFromHex`, and swaps ownership only on success.

## State and Persistence Behavior

Each instance owns `type` and `membuf` and deletes them in the destructor. `AsHexString()` uses a static output buffer, so the returned pointer is overwritten by later calls and is not thread-safe.

## Dependencies and Integration Points

It depends on `XrdSutAux` hex helpers, `XrdSutBucket`, and `XrdCryptoAux.hh`. Derived classes rely on its buffer/type ownership semantics.

## Risks and Edge Cases

`SetLength()` copies `l` bytes from the old buffer even when shrinking or when old `membuf` is null; if `l > lenbuf`, it can read past the old allocation before zero-filling the extension. `UseBuffer()` takes a `const char *` but later deletes it with `delete[]`, so callers must pass heap memory allocated compatibly and must not pass literals or stack memory. Static hex output is unsafe across threads.

## Test Signals

Tests should cover construction with null/empty buffers, `FromHex()` odd-length input, `SetLength()` grow/shrink from null and non-null buffers, ownership transfer with `UseBuffer()`, and concurrent `AsHexString()` calls.
