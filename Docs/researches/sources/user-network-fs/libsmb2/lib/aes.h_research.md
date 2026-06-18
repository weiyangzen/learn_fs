# sources/user-network-fs/libsmb2/lib/aes.h

## Purpose
`aes.h` declares the AES wrapper API used internally by libsmb2.

## Important APIs, Types, and Functions
It conditionally includes `config.h` when `HAVE_CONFIG_H` is defined, includes `compat.h`, and declares `void AES128_ECB_encrypt(uint8_t *input, const uint8_t *key, uint8_t *output);`.

## Control Flow
There is no runtime control flow. Include guards prevent duplicate declarations and configuration headers prepare fixed-width integer definitions before the prototype.

## State and Persistence Behavior
No state or persistence. The function declared here writes to caller-provided output.

## Dependencies and Integration Points
It depends on `compat.h` for portable integer types and is included by `aes.c` and crypto callers. It is listed in autotools sources and normal CMake source lists.

## Risks and Edge Cases
The API exposes raw pointers without size annotations, so all callers must provide 16-byte input, key, and output buffers. It is internal but not namespace-hidden beyond the function name.

## Test Signals
Compile all crypto users with `HAVE_CONFIG_H` on/off and run AES known-answer tests through the public wrapper.
