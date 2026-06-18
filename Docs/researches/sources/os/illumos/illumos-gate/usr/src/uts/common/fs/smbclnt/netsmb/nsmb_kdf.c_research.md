# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/nsmb_kdf.c

## Purpose

`nsmb_kdf.c` implements the SMB3 key derivation function described by MS-SMB2 and NIST SP800-108. It derives signing, application, encryption, and decryption keys from a session key, label, and context.

## Main Interfaces

The exported function is `nsmb_kdf(uint8_t *outbuf, uint32_t keylen, uint8_t *ssn_key, size_t ssn_keylen, uint8_t *label, size_t label_len, uint8_t *context, size_t context_len)`.

## Behavior And Data Flow

The function builds the fixed SP800-108 counter-mode input:

```text
counter || label || 0x00 || context || L
```

It uses a big-endian counter value of 1 and encodes output key length `L` in bits. Labels are limited to 16 bytes and contexts to 64 bytes, matching the fixed stack buffer. The PRF is HMAC-SHA256 using the session key. The resulting SHA-256 digest is copied to `outbuf` for the requested key length.

The file documents SMB 3.0.2 labels such as `SMB2AESCMAC`, `SMB2APP`, and `SMB2AESCCM`, and SMB 3.1.1 labels such as `SMBSigningKey`, `SMBS2CCipherKey`, and `SMBC2SCipherKey`.

## Dependencies

This file depends on `nsmb_hmac_getmech()` and `nsmb_hmac_one()` from the signing crypto layer, byte-order assumptions encoded manually into the KDF buffer, and constants from `nsmb_kcrypt.h`.

## Research Notes

The function asserts and fails on oversize label/context inputs. Callers must pass a `keylen` no larger than the SHA-256 digest length; current SMB callers derive 16- or 32-byte keys. The key-length field uses only the lower 16 bits after two zero bytes, which is suitable for current SMB key sizes.
