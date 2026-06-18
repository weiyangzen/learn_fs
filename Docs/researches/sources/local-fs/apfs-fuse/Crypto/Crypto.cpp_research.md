# File Research: sources/local-fs/apfs-fuse/Crypto/Crypto.cpp

## Role

`Crypto.cpp` provides higher-level crypto primitives built from the local AES, SHA-1, and SHA-256 implementations: RFC 3394 AES key wrap/unwrap, HMAC-SHA1, HMAC-SHA256, and PBKDF2-HMAC-SHA1/SHA256.

## Core Behavior

- `Rfc3394_KeyWrap()` wraps `size / 8` 64-bit plaintext blocks with six AES rounds and writes `A || R[1..n]`.
- `Rfc3394_KeyUnwrap()` reverses that process, optionally returns the recovered IV, and reports success only when the IV equals the RFC 3394 default `0xA6...A6`.
- `HMAC_SHA1()` and `HMAC_SHA256()` implement standard HMAC block-key normalization, inner hash, outer hash, and digest output.
- `PBKDF2_HMAC_SHA1()` and `PBKDF2_HMAC_SHA256()` derive up to one or two digest-sized blocks depending on requested length, appending big-endian block indices to the salt.

## Important Dependencies

- Uses `Crypto/Aes.h`, `Crypto/Sha1.h`, `Crypto/Sha256.h`, and `ApfsLib/Endian.h`.
- Used by APFS key-management code and encrypted disk-image handling.

## Notable Limitations And Risk Areas

- RFC 3394 code stores `r[6]`, so it only supports up to six 64-bit input blocks; callers must keep `size <= 48` bytes.
- RFC 3394 functions assume 64-bit aligned buffers through `reinterpret_cast<uint64_t *>`.
- Comments explicitly say the key-wrap code is not tested on big-endian machines.
- PBKDF2 functions rely on `assert()` for salt and derived-key size limits; those checks disappear in release builds.
- `PBKDF2_HMAC_SHA1()` permits salt up to `0x20` and derived key up to `0x20`; `PBKDF2_HMAC_SHA256()` permits salt up to `0x10` and derived key up to `0x20`.
- HMAC clears the temporary digest but does not clear `kdata`.
