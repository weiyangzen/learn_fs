# sources/storage-engines/lmdb/libraries/liblmdb/chacha8.c

## Purpose
Provides a public-domain ChaCha8 stream-cipher routine used by LMDB encryption test code. It XORs input data with a ChaCha8 keystream derived from a 32-byte key and 8-byte IV.

## Important APIs, Types, And Functions
The exported function is `chacha8(const void* data, size_t length, const uint8_t* key, const uint8_t* iv, char* cipher)`. Internal macros load/store little-endian 32-bit words, rotate, add modulo 32 bits, and perform the ChaCha quarter round. `sigma` supplies the `"expand 32-byte k"` constants.

## Control Flow
The function initializes the 16-word ChaCha state with constants, key words, a 64-bit block counter, and IV words. For each 64-byte block it copies partial final input into a temporary buffer when needed, performs eight rounds as four double-round iterations, adds the original state, XORs with input words, stores output, increments the counter, and advances pointers.

## State And Persistence Behavior
All cipher state is stack-local. The function writes only to the caller-provided output buffer and does not persist keys, IVs, or generated keystream.

## Dependencies And Integration Points
It includes `chacha8.h`, `<memory.h>`, `<stdio.h>`, and `<sys/param.h>` for `BYTE_ORDER`. The makefile links `chacha8.o` into `mtest_enc`.

## Risks And Edge Cases
The code casts byte pointers to `uint32_t*`, which can be sensitive to unaligned access and strict-aliasing assumptions on some platforms. Partial-block handling copies input to `tmp` and then copies the shortened output back. The comment leaves the 2^70-bytes-per-IV limit to callers. ChaCha8 is weaker than higher-round ChaCha variants and should be used only where that tradeoff is intended.

## Test Signals
No direct unit test appears in this subset. The encryption test programs built by the makefile are the expected functional signal.
