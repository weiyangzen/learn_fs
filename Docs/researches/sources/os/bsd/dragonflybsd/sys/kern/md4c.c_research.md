# File Research: sources/os/bsd/dragonflybsd/sys/kern/md4c.c

## Scope

This file is the in-kernel RSA Data Security MD4 message-digest implementation, adapted for DragonFlyBSD kernel headers and memory helpers.

## Public And Internal APIs Covered

- Public digest functions: `MD4Init()`, `MD4Update()`, `MD4Final()`.
- Internal helpers: `__kern__MD4Pad()`, `__kern__MD4Transform()`, `Encode()`, `Decode()`.
- MD4 round macros: `F`, `G`, `H`, `ROTATE_LEFT`, `FF`, `GG`, `HH`.

## Control Flow And Behavior

- `MD4Init()` zeroes the bit count and initializes the four MD4 state words to standard constants.
- `MD4Update()` updates the bit count, buffers partial blocks, transforms complete 64-byte blocks, and stores leftover bytes in the context buffer.
- `__kern__MD4Pad()` saves the original length, pads with `0x80` plus zero bytes to 56 mod 64, then appends the 64-bit little-endian length.
- `MD4Final()` pads, encodes the final 128-bit digest, and zeroes the context.
- `__kern__MD4Transform()` decodes one 64-byte block into sixteen 32-bit words, runs MD4's three rounds, adds the result back into the state, and zeroes the local block array.
- `Encode()` and `Decode()` explicitly convert between little-endian byte arrays and 32-bit words.

## State And Data Structures

- `MD4_CTX` stores `count[2]`, `state[4]`, and a 64-byte buffer.
- Static `PADDING[64]` supplies the MD-style padding block.

## Dependencies

- Includes `sys/md4.h` for context definition and uses kernel `bcopy()`/`bzero()` helpers.
- Suitable for kernel consumers needing MD4-compatible digest calculation, not for modern cryptographic security.

## Risks And Invariants

- Length accounting is 64-bit split across two 32-bit words and must be updated before buffering decisions.
- Encoding assumes MD4's required little-endian byte order independent of host representation.
- MD4 is cryptographically broken; this implementation should only be used for compatibility protocols or non-security checksums.
