<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/sha.h -->
# sources/user-network-fs/libsmb2/lib/sha.h

## Purpose

`sha.h` declares the bundled SHA and HMAC API used by libsmb2 cryptographic code. It is an RFC 4634-style interface covering SHA-256 and SHA-512 by default, optional SHA-1/SHA-224, optional SHA-384/SHA-512, a unified SHA selector, and HMAC state.

## Important APIs, Types, And Functions

The header defines return codes `shaSuccess`, `shaNull`, `shaInputTooLong`, `shaStateError`, and `shaBadParam`; hash/block sizes; `SHAversion`; contexts `SHA1Context`, `SHA256Context`, `SHA512Context`, aliases `SHA224Context` and `SHA384Context`, `USHAContext`, and `HMACContext`. It declares reset/input/final-bits/result functions for enabled algorithms, `USHA*` helpers, and `hmac*` helpers.

## Control Flow

The header is compile-time feature-gated by `USE_SHA1`, `USE_SHA224`, and `USE_SHA384_SHA512`. Consumers choose an algorithm either by calling the direct functions or by passing `SHAversion` to the unified/HMAC APIs.

## State And Persistence Behavior

Hash state is held in caller-owned contexts: intermediate digest words, bit length counters, pending message block, block index, and `Computed`/`Corrupted` flags. There is no persistence. Result calls finalize and mark contexts computed, after which more input is an error.

## Dependencies And Integration Points

It depends on config/stdlib/stdint availability and is implemented by `sha1.c`, `sha224-256.c`, `sha384-512.c`, and separate unified/HMAC implementation files elsewhere in libsmb2. SMB3 signing, preauth integrity, and key derivation code are likely consumers.

## Risks And Edge Cases

Default macros disable SHA-1 and SHA-224 while enabling SHA-384/512, so build configurations must match callers. Context layouts differ under `USE_32BIT_ONLY`. The API supports final partial bits, which is easy to misuse. It does not provide constant-time comparison or automatic context cleansing beyond implementation finalizers clearing message blocks.

## Test Signals

Compile matrix tests should cover feature macro combinations and `USE_32BIT_ONLY`. Runtime tests need NIST known-answer vectors, incremental input in varied chunk sizes, final-bit inputs, post-result input errors, null argument errors, and HMAC vectors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/sha.h -->
