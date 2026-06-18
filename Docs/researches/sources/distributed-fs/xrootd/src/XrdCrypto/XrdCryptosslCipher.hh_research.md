<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslCipher.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslCipher.hh

## Purpose
Declares `XrdCryptosslCipher`, the OpenSSL implementation of the generic `XrdCryptoCipher` interface. It defines the object state and public methods used for symmetric encryption, IV handling, serialization, and DH key agreement.

## Important APIs, types, and functions
- Private state includes `fIV`, `lIV`, `cipher`, `ctx`, `fDH`, `deflength`, and `valid`.
- Constructors support generated ciphers, imported key/IV ciphers, bucket-imported ciphers, DH key agreement, and copy construction.
- `Finalize()` completes DH agreement after receiving a peer public key.
- `Cleanup()` releases DH temporary state.
- `IsSupported()` queries OpenSSL cipher availability.
- `EncOutLength()`, `DecOutLength()`, `Public()`, `AsBucket()`, `IV()`, `IsDefaultLength()`, and `MaxIVLength()` expose metadata and serialization.
- `SetIV()`, `Encrypt()`, `Decrypt()`, and `RefreshIV()` mutate/use cipher state.

## Control flow
The header defines the operational contract used by the implementation: construct to set valid state, optionally exchange public DH buffers and finalize, then call encrypt/decrypt with caller-sized buffers. The static support check lets the factory reject unsupported algorithms before object creation.

## State and persistence behavior
Instances hold OpenSSL contexts and keys. The `IV()` accessor and `RefreshIV()` expose internal IV memory, so callers must not free or mutate it unexpectedly. `AsBucket()` creates persistent transport state for the cipher; because private key bytes can be serialized by the implementation, buckets must be treated as secrets.

## Dependencies and integration points
Inherits from `XrdCryptoCipher` and includes OpenSSL `evp.h` and `dh.h`. It is constructed only through `XrdCryptosslFactory` in normal plugin use, but the class is also visible to nearby implementation files and tests.

## Risks and edge cases
The class exposes raw pointers for IV and public buffers, so ownership conventions must be documented and tested. The header's private helper `PrintPublic()` is debug-only but still part of class shape. The commented-out `kDHMINBITS` notes historical dynamic DH generation; reviewers should look at the implementation before re-enabling any dynamic parameter generation.

## Test signals
Interface tests should verify `IsValid()` after all constructors, `Public()` ownership/length behavior, IV length reporting, copy construction, and factory downcast assumptions in `XrdCryptosslFactory::Cipher(const XrdCryptoCipher&)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslCipher.hh -->
