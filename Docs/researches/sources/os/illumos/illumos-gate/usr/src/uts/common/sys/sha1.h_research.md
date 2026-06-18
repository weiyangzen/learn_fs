# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sha1.h

## Role

Declares SHA-1 context layout and incremental hashing functions.

## Key Interfaces

- `SHA1_CTX` contains:
  - `uint32_t state[5]`
  - `uint32_t count[2]`
  - 64-byte buffered input union as bytes or aligned words
- Constants:
  - `SHA1_BLOCK_LENGTH` = 64
  - `SHA1_DIGEST_LENGTH` = 20
- Functions:
  - `SHA1Init()`
  - `SHA1Update()`
  - `SHA1Final()`

## Compatibility Notes

The file warns that the Niagara2 RNG driver directly accesses `SHA1_CTX::state`; it must remain a `uint32_t state[5]`.

## Risk Notes

Despite being a hash context, the structure layout is consumed directly by another driver. Reordering or resizing fields can break kernel consumers.
