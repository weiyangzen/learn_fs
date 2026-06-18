# sources/user-network-fs/libsmb2/lib/hmac-md5.h

## Purpose
`hmac-md5.h` declares libsmb2's HMAC-MD5 helper and provides compatibility typedef setup needed by the bundled MD5 code on supported platforms.

## Important APIs, Types, and Functions
The public declaration is `smb2_hmac_md5(...)`, which computes a 16-byte MD5 HMAC into a caller-owned buffer. The header conditionally includes `config.h`, `string.h`, `sys/types.h`, and `stdint.h`, defines `WORDS_BIGENDIAN` for big-endian or Xbox builds, and defines `UWORD32` as `uint32_t` unless excluded for PS2 or Pico platforms.

## Control Flow
There is no runtime control flow. Preprocessor branches select platform configuration and C++ linkage. The `extern "C"` block makes the function callable from C++ translation units without name mangling.

## State and Persistence Behavior
The header has no runtime state. Its main persistent effect is compile-time: it can define `WORDS_BIGENDIAN` and `UWORD32_DEFINED`, which may affect included or neighboring crypto compilation units.

## Dependencies and Integration Points
It is included by callers that need the one-shot MD5 HMAC routine implemented in `hmac-md5.c`. The `UWORD32` and endian definitions are compatibility glue for the MD5 implementation rather than SMB protocol logic.

## Risks and Edge Cases
The comment says `RFC1204` although HMAC-MD5 is normally associated with RFC 2104. The endian macro relies on `__BYTE_ORDER`/`__BIG_ENDIAN` being available from prior configuration headers. Because the function signature does not use `const`, callers may be forced to cast const buffers even though the implementation does not mutate them.

## Test Signals
Compile tests should cover C and C++ consumers, big-endian macro paths, platforms without `stdint.h`, and callers that include the header before MD5-related headers. API tests should verify the digest size contract through `smb2_hmac_md5()` known-answer vectors.
