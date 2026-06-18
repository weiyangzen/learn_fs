# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoRSA.cc

## Purpose

`XrdCryptoRSA.cc` implements the abstract RSA base defaults plus bucket/string convenience wrappers for public/private key export and encryption/decryption.

## Important APIs and Functions

The base virtual methods (`Dump`, `Opaque`, output length queries, import/export, and raw encrypt/decrypt methods) log `ABSTRACTMETHOD` and fail. `ExportPublic(XrdOucString &)`, `ExportPrivate(XrdOucString &)`, and bucket wrappers allocate temporary buffers based on concrete output lengths, call raw virtual methods, and update the target string or bucket on success.

## Control Flow

Export wrappers request a concrete length, allocate one extra byte for NUL termination, zero-fill, call concrete export, copy into `XrdOucString`, and delete the temporary. Bucket wrappers allocate `GetOutlen(bck.size)`, perform the selected raw RSA operation, and update the bucket if the result size is nonnegative.

## State and Persistence Behavior

The base class stores only `status`, with static string names `Invalid`, `Public`, and `Complete`. Concrete subclasses own key material and opaque backend objects.

## Dependencies and Integration Points

It depends on `XrdCryptoRSA.hh`, `XrdSutBucket`, and `XrdOucString`. Factories create concrete RSA objects for key exchange, signing-like operations, and certificate handling.

## Risks and Edge Cases

The bucket wrappers rely on `GetOutlen()` returning positive sane lengths; zero or negative lengths can lead to bad allocation behavior. On raw operation failure, wrappers delete the temporary buffer; on success they assume `XrdSutBucket::Update()` assumes ownership. RSA operation naming exposes private-key encryption/public-key decryption patterns that need careful use as signature primitives rather than confidentiality.

## Test Signals

Concrete RSA tests should cover key generation/import/export, public-only versus complete status, all bucket wrappers, failure cleanup, and max input size behavior.
