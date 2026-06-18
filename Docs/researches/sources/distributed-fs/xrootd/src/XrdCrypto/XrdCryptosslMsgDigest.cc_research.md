<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslMsgDigest.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslMsgDigest.cc

## Purpose
Implements `XrdCryptosslMsgDigest`, an OpenSSL EVP message digest wrapper for the generic `XrdCryptoMsgDigest` interface. It supports digest algorithm lookup, incremental update, finalization into the inherited buffer, and reset.

## Important APIs, types, and functions
- Constructor initializes type and calls `Init()`.
- Destructor finalizes any valid digest context and destroys `mdctx`.
- `IsSupported()` checks `EVP_get_digestbyname`.
- `Init()` selects the requested digest or default `sha256`, allocates an `EVP_MD_CTX`, and initializes it.
- `Reset()` finalizes/discards current state, clears the output buffer, destroys the old context, and reinitializes.
- `Update()` calls `EVP_DigestUpdate`.
- `Final()` calls `EVP_DigestFinal_ex`, stores the result in the base buffer, and emits debug output.

## Control flow
Construction sets the digest type to null, then `Init()` chooses caller type or default. Updates are accepted when `Type()` is set. Finalization stores the digest bytes in the inherited buffer for later access such as hex string conversion. Reset finalizes the existing context even if the caller never asked for the digest, then recreates a new context.

## State and persistence behavior
The object owns `EVP_MD_CTX *mdctx`, a `valid` flag, and inherited type/output buffer state. No durable persistence exists. The digest result persists in the object's base buffer after `Final()` until reset/destruction.

## Dependencies and integration points
Depends on OpenSSL EVP digest APIs, `XrdCryptoMsgDigest`, generic crypto helpers, and trace macros. `XrdCryptosslFactory` constructs this class and uses `IsSupported()`.

## Risks and edge cases
`Update()` checks `Type()` rather than `valid` or `mdctx`, so a failed `Init()` that left a type string could lead to use of a null/destroyed context. `Init()` does not check `EVP_MD_CTX_create()` before `EVP_DigestInit_ex`. Destructor and reset both call finalization to discard state, which can fail silently or mutate OpenSSL error state. The error message in `Init()` has a typo but also uses `PRINT` rather than returning structured error details.

## Test signals
Tests should compare SHA-256 and other algorithm outputs to known vectors, validate unsupported digest handling, call `Update()` and `Final()` in invalid states under ASAN, reset between algorithms, and verify factory support queries match construction results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslMsgDigest.cc -->
