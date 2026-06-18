# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cryptmod.h

## Role

Defines a Sun-private STREAMS crypto module interface, including ioctls, method identifiers, setup structures, and kernel module state.

## Ioctls

Base:

- `CRYPTIOC`

Commands:

- `CRYPTIOCSETUP`
- `CRYPTIOCSTOP`
- `CRYPTIOCSTARTENC`
- `CRYPTIOCSTARTDEC`
- `CRYPTPASSTHRU`

## Methods

- `CRYPT_METHOD_NONE`
- DES CFB/CBC variants.
- 3DES CBC SHA1.
- ARCFOUR HMAC MD5 and export variant.
- AES128/AES256.

Validation/helper macros:

- `CR_METHOD_OK()`
- `IS_RC4_METHOD()`
- `IS_AES_METHOD()`

## Direction and IV Usage

- Directions:
  - `CRYPT_ENCRYPT`
  - `CRYPT_DECRYPT`
  - `CR_DIRECTION_OK()`
- IV usage:
  - `IVEC_NEVER`
  - `IVEC_REUSE`
  - `IVEC_ONETIME`
  - `CR_IVUSAGE_OK()`

## Sizes and Options

Defines SHA1, DES3, ARCFOUR, AES key/hash/block sizes, truncated AES HMAC length, and max key/IV lengths.

Options:

- `CRYPTOPT_NONE`
- `CRYPTOPT_RCMD_MODE_V1`
- `CRYPTOPT_RCMD_MODE_V2`
- `ANY_RCMD_MODE()`
- `RCMD_LEN_SZ`
- `CR_OPTIONS_OK()`

## User Setup Structure

- `struct cr_info_t`:
  - key and IV buffers.
  - key/IV lengths.
  - IV usage.
  - direction mask.
  - crypto method.
  - option mask.

## Kernel State

Under `_KERNEL`:

- Usage constants for rcmd, ARCFOUR, AES.
- Default block sizes and ARCFOUR export salt.
- `struct cipher_data_t`: key/block/IV/saveblock buffers, mechanism type, crypto keys/templates/context, byte counts, lengths, IV usage, method, options.
- `struct rcmd_state_t`: plaintext/cipher lengths, received count, next length, mblk accumulator.
- Ready masks: `CRYPT_WRITE_READY`, `CRYPT_READ_READY`.
- `struct tmodinfo`: encryption/decryption cipher data, rcmd state, ready mask.

## Research Relevance

Documents legacy STREAMS encryption behavior and how it bridges to the kernel crypto API. Relevant for historical secure r-command paths and STREAMS data transformation.
