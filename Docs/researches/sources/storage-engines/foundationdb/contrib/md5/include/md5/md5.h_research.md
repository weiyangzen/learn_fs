# sources/storage-engines/foundationdb/contrib/md5/include/md5/md5.h

## Purpose
`md5.h` declares an OpenSSL-compatible MD5 API, either by including OpenSSL's header when `HAVE_OPENSSL` is defined or by declaring the bundled implementation's types and functions.

## Important APIs, Types, And Functions
When OpenSSL is unavailable, it defines `MD5_u32plus`, `MD5_CTX` with counters, hash state words, a 64-byte buffer, and a 16-word block buffer. It declares `MD5_Init`, `MD5_Update`, and `MD5_Final` with `MULTIPLY_DEFINED_SYMBOL` from `flow/Platform.h`.

## Control Flow
The header is controlled by preprocessor branches. With `HAVE_OPENSSL`, it delegates to `<openssl/md5.h>`; otherwise it exposes bundled declarations behind `_MD5_H`.

## State And Persistence Behavior
`MD5_CTX` is caller-owned incremental digest state. No persistence is involved.

## Dependencies And Integration Points
It depends on OpenSSL when configured, otherwise on `flow/Platform.h` for symbol annotation. `md5.c` implements the non-OpenSSL declarations. The function names intentionally match OpenSSL for compatibility.

## Risks And Edge Cases
The header name guard `_MD5_H` can overlap with other MD5 headers. `MD5_u32plus` is `unsigned int`, assuming it is at least 32 bits. MD5 should not be used for security-sensitive integrity. Symbol compatibility depends on `MULTIPLY_DEFINED_SYMBOL`.

## Test Signals
Compile tests should cover both `HAVE_OPENSSL` and bundled paths. Functional tests should hash standard vectors through init/update/final and compare with known digests.
