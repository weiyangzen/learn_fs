# File Research: sources/local-fs/apfs-fuse/Crypto/Sha1.cpp

## Role

`Sha1.cpp` implements SHA-1 hashing for local HMAC/PBKDF2 and disk-image compatibility code.

## Core Behavior

- `Init()` sets the SHA-1 initial hash constants, clears the bit count and buffer index, and zeros the 64-byte buffer.
- `Update()` appends bytes to the block buffer, processes full 64-byte blocks with `Round()`, and increments the bit count.
- `Final()` appends SHA-1 padding, writes the 64-bit big-endian message length, processes the last block, and writes a 20-byte digest.
- `Round()` expands 16 message words to 80 and runs the four SHA-1 round families using `Ch`, `Parity`, and `Maj`.

## Important Dependencies

- Implements `Crypto/Sha1.h`.
- Used by `Crypto/Crypto.cpp` for HMAC-SHA1 and PBKDF2-HMAC-SHA1.
- Used by disk-image code for older encrypted image formats.

## Notable Limitations And Risk Areas

- SHA-1 is collision-broken and should only be used where compatibility requires it.
- `Final()` does not call `Init()` afterward, so object reuse requires an explicit `Init()`.
- No secure clearing is performed for internal buffers after finalization.
