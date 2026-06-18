# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/hkdf.c

## Role

Implements HKDF-SHA512 for ZFS encryption key derivation using the illumos kernel crypto API.

## Extract

`hkdf_sha512_extract()` computes HMAC-SHA512 with the salt as the raw crypto key and input key material as data. It writes the pseudorandom key to a SHA-512 digest-sized output buffer and maps crypto failures to `EIO`.

## Expand

`hkdf_sha512_expand()` uses the extracted key as the HMAC key and iteratively computes HKDF blocks over `T(previous) || info || counter`. It copies each block into the output buffer, with the final block truncated to remaining output length. It rejects more than 255 blocks.

A detail to preserve: the block count is computed as `(out_len + SHA512_DIGEST_LENGTH) / SHA512_DIGEST_LENGTH`, which is one higher than the usual ceiling formula for exact digest-size multiples. That causes an extra zero-byte-copy HMAC round for exact multiples and rejects the theoretical maximum exact length one block early.

## Public API

`hkdf_sha512()` runs extract then expand and returns the first error, or `0` on success.

## Usage Context

The file comment states this is used to derive fresh encryption keys from a master key and salt to avoid cryptographic limits of underlying encryption modes. It notes that elsewhere in the code the HKDF `info` parameter is commonly referred to as “salt”.
