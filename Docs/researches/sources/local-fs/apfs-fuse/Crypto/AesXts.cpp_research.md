# File Research: sources/local-fs/apfs-fuse/Crypto/AesXts.cpp

## Role

`AesXts.cpp` implements AES-XTS-style sector/unit encryption using two AES-128 keys. It is the data-encryption primitive used by APFS volume handling.

## Core Behavior

- `CleanUp()` clears both embedded AES instances.
- `SetKey()` installs `key1` into the data AES instance and `key2` into the tweak AES instance, both as AES-128.
- `Encrypt()` builds the initial tweak from little-endian `unit_no || 0`, encrypts it with key2, then loops over 16-byte blocks:
  - XOR plaintext with tweak.
  - AES-encrypt with key1.
  - XOR with tweak to produce ciphertext.
  - Multiply tweak by `x` in GF(2^128).
- `Decrypt()` mirrors the same tweak flow but AES-decrypts the middle block.
- `MultiplyTweak()` handles little-endian and big-endian hosts separately using APFS endian helpers.

## Important Dependencies

- Depends on `Crypto/Aes.h`.
- Uses `ApfsLib/Endian.h` for host/little-endian conversions.
- Referenced by `ApfsLib/ApfsVolume` and APFS dump tooling.

## Notable Limitations And Risk Areas

- Only AES-128 XTS keys are supported by `SetKey()`.
- There is no ciphertext stealing support; `size` must be a multiple of 16.
- The function loops in 16-byte increments without validating `size`, so non-block-aligned input can overread/overwrite.
- `Xor128()` casts arbitrary pointers to `uint64_t *`, which can be unaligned and can violate strict-aliasing assumptions on some platforms.
