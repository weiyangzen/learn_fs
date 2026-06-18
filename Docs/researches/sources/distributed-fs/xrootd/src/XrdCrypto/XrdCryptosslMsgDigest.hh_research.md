<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslMsgDigest.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslMsgDigest.hh

## Purpose
Declares the OpenSSL implementation of `XrdCryptoMsgDigest`, providing the small object interface for digest support checks, reset/update/final operations, and validity.

## Important APIs, types, and functions
- Private `valid` flag and `EVP_MD_CTX *mdctx` hold OpenSSL digest state.
- `Init()` is a private helper for constructor and reset.
- Public constructor/destructor, `IsValid()`, static `IsSupported()`, `Reset()`, `Update()`, and `Final()` implement the generic digest contract.

## Control flow
The header exposes the standard incremental digest lifecycle: construct or reset, update with one or more buffers, and finalize to populate inherited output state.

## State and persistence behavior
Digest state is in memory only. The class owns its OpenSSL context and inherited digest result buffer.

## Dependencies and integration points
Includes OpenSSL `evp.h` and `XrdCryptoMsgDigest.hh`. It is instantiated by `XrdCryptosslFactory` and used wherever generic `XrdCryptoMsgDigest` pointers are consumed.

## Risks and edge cases
Raw context ownership means copy behavior is intentionally absent; accidental copying by value would be unsafe if ever introduced. Validity is exposed but callers still need to observe return codes from `Update()` and `Final()`.

## Test signals
Header-level tests should include construction through the factory, `IsSupported()` for known and invalid digest names, and compile checks that consumers can use only the generic base methods where intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslMsgDigest.hh -->
