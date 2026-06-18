# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoLite.cc

## Purpose

`XrdCryptoLite.cc` implements the static factory for the lightweight crypto interface, currently dispatching only the `bf32` algorithm.

## Important APIs and Functions

`XrdCryptoLite::Create(int &rc, const char *Name, const char Type)` declares the external constructor `XrdCryptoLite_New_bf32()`, compares `Name` with `"bf32"`, creates the implementation, sets `rc` to zero on success or `EPROTONOSUPPORT` on failure, and returns the pointer.

## Control Flow

The function is a simple name-dispatch table. Adding an algorithm requires declaring its constructor and adding a comparison branch.

## State and Persistence Behavior

No persistent state is maintained here. The returned object is caller-owned.

## Dependencies and Integration Points

It depends on `<cerrno>`, `<cstring>`, and `XrdCryptoLite.hh`. `XrdCryptoLite_bf32.cc` supplies the concrete external constructor.

## Risks and Edge Cases

`Name` is passed directly to `strcmp()` with no null check, so a null algorithm name crashes. Unsupported algorithms all map to `EPROTONOSUPPORT`.

## Test Signals

Tests should verify `bf32` creation, unsupported name failure, null-name handling expectations, type echoing, and caller deletion of returned objects.
