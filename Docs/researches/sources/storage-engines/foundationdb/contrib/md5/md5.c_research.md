# sources/storage-engines/foundationdb/contrib/md5/md5.c

## Purpose
`md5.c` implements the bundled OpenSSL-compatible MD5 message-digest algorithm when `HAVE_OPENSSL` is not defined.

## Important APIs, Types, And Functions
The file defines MD5 round functions `F`, `G`, `H`, `H2`, `I`, the `STEP` macro, endian-aware `SET`/`GET` macros, static `body(MD5_CTX*, const void*, unsigned long)` for 64-byte block transforms, and public `MD5_Init`, `MD5_Update`, and `MD5_Final`.

## Control Flow
`MD5_Init` sets the four standard initial state words and zeroes bit counters. `MD5_Update` updates byte counters, fills any partial buffer, processes full 64-byte blocks with `body`, and stores remaining bytes. `MD5_Final` appends `0x80`, zero padding, the bit length, processes the final block, writes the 16-byte little-endian digest, and zeroes the context. `body` applies all four MD5 rounds to one or more 64-byte blocks.

## State And Persistence Behavior
Digest state lives entirely in caller-provided `MD5_CTX`. Finalization clears the context with `memset`. No external persistence occurs.

## Dependencies And Integration Points
It includes `<string.h>` and `md5.h`, and is excluded at compile time when `HAVE_OPENSSL` is defined. The CMake target builds it into the `md5` static library.

## Risks And Edge Cases
MD5 is not collision-resistant and must not be used for security decisions. The x86/vax `SET` macro reads unaligned words by casting, which is fast but can violate strict aliasing expectations on some compilers. The counter uses a 29-bit low byte count plus high count scheme matching the original implementation; very large inputs should be covered by tests.

## Test Signals
Tests should run RFC 1321 vectors, incremental updates with all chunk sizes, large input crossing many blocks, empty input, finalization clearing behavior if observable, and parity with OpenSSL when available.
