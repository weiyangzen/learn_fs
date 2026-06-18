# sources/user-network-fs/libsmb2/lib/md5.h

## Purpose

`md5.h` declares the bundled MD5 context and functions used by libsmb2 crypto helpers, especially HMAC-MD5 for NTLMSSP. It preserves the Colin Plumb public-domain MD5 API while adapting integer and endian definitions to this project's portability layer.

## Important APIs, Types, And Functions

The header defines `md5byte` as `unsigned char`, `UWORD32` as `uint32_t` when not already defined and not on excluded targets, and `struct MD5Context` with `buf[4]`, `bytes[2]`, and `in[16]`. It declares `MD5Init`, `MD5Update`, `MD5Final`, and `MD5Transform`, with C++ linkage guards.

## Control Flow

Consumers allocate a `struct MD5Context`, initialize it, call `MD5Update` for one or more byte ranges, and finalize into a 16-byte digest. `MD5Transform` is exposed for code that wants direct block compression, though normal callers should use the streaming API.

## State And Persistence Behavior

The header defines only caller-owned in-memory state. No persistent storage or global state is introduced. The implementation clears the context during finalization.

## Dependencies And Integration Points

The header includes `config.h` when available, optional `netinet/in.h`, `string.h`, `sys/types.h`, and `stdint.h`. It derives `WORDS_BIGENDIAN` from `__BYTE_ORDER` or `XBOX_360_PLATFORM`. Its direct integration is `md5.c`; higher-level use is through HMAC-MD5 and NTLMSSP response generation/verification.

## Risks And Edge Cases

The preprocessor expression for `WORDS_BIGENDIAN` depends on platform macros being defined consistently. Targets without `uint32_t` or with `PS2_IOP_PLATFORM` need compatible `UWORD32` definitions elsewhere. MD5 is legacy cryptography and should not be exposed as a recommended hashing primitive outside protocol compatibility code.

## Test Signals

Compile on little-endian, big-endian, C, and C++ builds. Verify MD5 known vectors through the public API and run HMAC-MD5/NTLMSSP integration tests to ensure the context layout and endian settings match `md5.c`.
