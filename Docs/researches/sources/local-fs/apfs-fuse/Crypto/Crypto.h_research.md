# File Research: sources/local-fs/apfs-fuse/Crypto/Crypto.h

## Role

`Crypto.h` declares the repository's higher-level crypto utility functions.

## Public Interface

- `Rfc3394_KeyWrap()` wraps key material using AES and a caller-supplied IV.
- `Rfc3394_KeyUnwrap()` unwraps key material, returns plaintext, optionally returns the recovered IV, and validates the default wrap IV.
- `HMAC_SHA1()` and `HMAC_SHA256()` compute message authentication codes.
- `PBKDF2_HMAC_SHA1()` and `PBKDF2_HMAC_SHA256()` derive key bytes from password/salt/iteration inputs.

## Important Dependencies

- Includes `Crypto/Aes.h` for AES mode selection in RFC 3394 wrappers.

## Notable Limitations And Risk Areas

- The header does not express maximum supported sizes for RFC 3394 or PBKDF2 buffers.
- All functions are raw-pointer APIs and rely on callers to provide valid, sufficiently sized buffers.
