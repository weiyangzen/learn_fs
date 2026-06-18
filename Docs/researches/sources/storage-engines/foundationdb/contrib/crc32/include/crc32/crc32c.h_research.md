# sources/storage-engines/foundationdb/contrib/crc32/include/crc32/crc32c.h

## Purpose
Public C-compatible declaration for CRC-32C append computation.

## Important APIs, Types, And Functions
Declares `extern "C" uint32_t crc32c_append(uint32_t crc, const uint8_t* input, size_t length);`. Documents Castagnoli polynomial `0x82f63b78`, accumulation across buffers, and hardware fallback behavior.

## Control Flow
Header-only declaration and documentation.

## State And Persistence
No state.

## Dependencies And Integration
Includes `<stdint.h>` and `<stdlib.h>`. Consumed by C++ and C-compatible callers linking against the `crc32` target.

## Risks
The unconditional `extern "C"` requires C++ compilation; a pure C compiler would not accept it. The header uses `size_t` from `<stdlib.h>` rather than `<stddef.h>`, which is normally sufficient but less direct.

## Test Signals
Compile from a C++ consumer, link, and verify incremental CRC append behavior. If C consumers are expected, add a C compatibility compile test.
