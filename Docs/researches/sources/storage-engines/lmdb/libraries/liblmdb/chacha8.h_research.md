# sources/storage-engines/lmdb/libraries/liblmdb/chacha8.h

## Purpose
Declares the small ChaCha8 helper API used by LMDB encryption tests.

## Important APIs, Types, And Functions
The header defines `CHACHA8_KEY_SIZE` as 32, `CHACHA8_IV_SIZE` as 8, includes `<stdint.h>` and `<stddef.h>`, and declares `chacha8(const void*, size_t, const uint8_t*, const uint8_t*, char*)`.

## Control Flow
There is no executable control flow. Callers provide input data, byte length, key, IV, and output buffer.

## State And Persistence Behavior
The API is stateless from the caller perspective; all state lives inside the implementation call. The caller owns key, IV, input, and output memory.

## Dependencies And Integration Points
`chacha8.c` implements this declaration, and the makefile compiles it for `mtest_enc`. The constants document the required key and IV buffer sizes.

## Risks And Edge Cases
The function signature does not encode buffer sizes for key, IV, or output; callers must allocate correctly. It has no namespace prefix beyond the function name and can collide in larger C link contexts.

## Test Signals
Build success catches declaration/definition drift. Runtime encryption tests catch basic behavioral issues.
