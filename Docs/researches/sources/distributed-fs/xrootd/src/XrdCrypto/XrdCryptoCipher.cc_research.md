# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoCipher.cc

## Purpose

`XrdCryptoCipher.cc` provides the abstract symmetric-cipher base implementation and bucket-level convenience wrappers for encryption and decryption.

## Important APIs and Functions

Most virtual methods (`Finalize`, `IsValid`, `SetIV`, `RefreshIV`, `IV`, `Public`, `AsBucket`, raw `Encrypt`/`Decrypt`, output-length queries, default-length check, and max-IV query) log `ABSTRACTMETHOD` and return failure defaults. The concrete logic is in `Encrypt(XrdSutBucket &, bool)` and `Decrypt(XrdSutBucket &, bool)`, which allocate output buffers, optionally prepend/extract IVs, call raw virtual methods, and update buckets.

## Control Flow

For bucket encryption, the wrapper refreshes an IV when requested, allocates `EncOutLength(size) + liv`, copies the IV prefix, encrypts into the remaining buffer, and updates the bucket when raw encryption succeeds. For bucket decryption, it treats `MaxIVLength()` bytes as the IV prefix, calls `SetIV()`, decrypts the rest, and updates the bucket on success.

## State and Persistence Behavior

The base class has no cipher state beyond inherited `XrdCryptoBasic` storage. Concrete subclasses are responsible for key, IV, padding, and public key-agreement state.

## Dependencies and Integration Points

It depends on `XrdCryptoAux.hh`, `XrdCryptoCipher.hh`, and `XrdSutBucket`. Crypto factory implementations return concrete subclasses through the abstract interface.

## Risks and Edge Cases

On encryption, if raw `Encrypt()` fails after allocation, `newbck` is not deleted, creating a leak. On decryption, `bck.size - liv` can become negative if the bucket is shorter than the IV length, which can produce bad output-length requests. Wrapper ownership relies on `XrdSutBucket::Update()` taking ownership of `newbck`.

## Test Signals

Mock cipher subclasses should test IV prefix handling, update ownership, failure paths, short bucket decryption, and output-length calculations.
