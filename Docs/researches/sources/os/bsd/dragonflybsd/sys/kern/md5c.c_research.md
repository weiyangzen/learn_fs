# File Research: sources/os/bsd/dragonflybsd/sys/kern/md5c.c

## Scope

This file is the DragonFlyBSD in-kernel MD5 implementation, derived from RSA Data Security code and intended to stay in sync with the userland `libmd` implementation.

## Public And Internal APIs Covered

- Public digest functions: `MD5Init()`, `MD5Update()`, `MD5Final()`.
- Internal helpers: `__kern__MD5Pad()`, `__kern__MD5Transform()`, and endian-dependent `Encode()`/`Decode()` helpers.
- MD5 round macros: `F`, `G`, `H`, `I`, `ROTATE_LEFT`, `FF`, `GG`, `HH`, `II`.

## Control Flow And Behavior

- `MD5Init()` initializes the bit counters and standard MD5 state words, returning `1`.
- `MD5Update()` updates the 64-bit bit count in `Nl`/`Nh`, fills any partial 64-byte block, transforms complete blocks, and buffers the remainder.
- On little-endian machines, `Encode` and `Decode` are aliases for `memcpy`; otherwise explicit byte-order conversion is compiled in.
- `__kern__MD5Pad()` saves the bit length, pads to 56 mod 64, and appends the saved length.
- `MD5Final()` pads, encodes the four-word state into the 16-byte digest, and clears the context.
- `__kern__MD5Transform()` runs the standard 64 MD5 operations across four rounds and adds the transformed state back into the context.

## State And Data Structures

- `MD5_CTX` contains state words `A` through `D`, counters `Nl`/`Nh`, and a data buffer.
- Static `PADDING[64]` contains the `0x80` prefix and zero fill.

## Dependencies

- Builds both in-kernel and outside the kernel: kernel builds use `sys/systm.h`, non-kernel builds use `<string.h>`.
- Includes endian headers and `sys/md5.h`.

## Risks And Invariants

- MD5 byte order is little-endian; non-little-endian platforms depend on the explicit conversion helpers.
- The context is zeroed after finalization, so callers must not reuse it without `MD5Init()`.
- MD5 is cryptographically broken and should be treated as compatibility/checksum code rather than a secure digest.
