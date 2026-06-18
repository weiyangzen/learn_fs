# sources/user-network-fs/libsmb2/lib/hmac.c

## Purpose
`hmac.c` implements RFC 2104 HMAC over the SHA family described by the repository's RFC 4634-style SHA abstraction. It supports one-shot and streaming HMAC computation for SHA-1, SHA-224, SHA-256, SHA-384, and SHA-512 through the `USHA` interface.

## Important APIs, Types, and Functions
The exported API includes `hmac()`, `hmacReset()`, `hmacInput()`, `hmacFinalBits()`, and `hmacResult()`. The main state type is `HMACContext`, defined with SHA context fields in `sha.h`. The code uses `SHAversion`, `USHAContext`, `USHABlockSize()`, `USHAHashSize()`, `USHAReset()`, `USHAInput()`, `USHAFinalBits()`, and `USHAResult()`.

## Control Flow
`hmac()` is a one-shot wrapper that resets a stack context, feeds the entire message, and finalizes the digest. `hmacReset()` validates the context, records the selected SHA variant, hashes overlong keys down to the selected hash length, builds inner and outer pads for the selected block size, stores the outer pad in `ctx->k_opad`, and starts the inner SHA pass with the inner pad. `hmacInput()` streams message bytes into the inner SHA context. `hmacFinalBits()` forwards final non-byte-aligned bits. `hmacResult()` finalizes the inner digest into the caller's digest buffer, reinitializes SHA, hashes the outer pad plus inner digest, and writes the final HMAC.

## State and Persistence Behavior
HMAC state is fully caller-owned through `HMACContext`. The context persists the selected SHA version, block/hash sizes, inner SHA state, and outer pad between reset and result. The one-shot wrapper uses only stack state. Temporary keys and pads are not wiped after use.

## Dependencies and Integration Points
The file depends on `compat.h`, `sha.h`, optional `config.h`, `stdint.h`, and `stdlib.h`. It is a generic crypto primitive for libsmb2 signing/key derivation paths that require HMAC-SHA, especially SMB2/SMB3 authentication and session security code elsewhere in the library.

## Risks and Edge Cases
Most functions check only for a NULL context, not NULL key, text, or digest pointers. Error propagation relies on logical OR chaining; callers receive the first nonzero SHA error but not detailed stage context. `hmacResult()` uses the caller's digest buffer as a temporary inner digest, so the buffer must be at least `USHAMaxHashSize` or at least the selected hash size as required by the SHA API. Key material remains in stack/context memory until overwritten.

## Test Signals
Use RFC 4231/RFC 4634 HMAC-SHA known-answer vectors across SHA-1/SHA-256/SHA-512, including long keys, empty messages, streaming input split across several calls, `hmacFinalBits()`, NULL context returns, and digest agreement between one-shot `hmac()` and reset/input/result sequences.
