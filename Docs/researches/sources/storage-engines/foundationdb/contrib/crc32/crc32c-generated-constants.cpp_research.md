# sources/storage-engines/foundationdb/contrib/crc32/crc32c-generated-constants.cpp

## Purpose
Generated C++ constants for the CRC-32C implementation in `crc32c.cpp`.

## Important APIs, Types, And Functions
Defines `POLY 0x82f63b78`, `LONG_SHIFT 8192`, `SHORT_SHIFT 256`, `table[16][256]`, `long_shifts[4][256]`, and `short_shifts[4][256]`. These arrays are declared `static` and consumed by inclusion into `crc32c.cpp`.

## Control Flow
There is no executable control flow. The compiler initializes static lookup tables used by software CRC and hardware block-combination paths.

## State And Persistence
Read-only process-local static data. No persistence or mutation.

## Dependencies And Integration
Included directly by `crc32c.cpp`, not compiled as an independent translation unit. Generated from Mark Adler / Robert Vazan CRC32C algorithms and marked as altered from original.

## Risks
Manual edits can corrupt CRC correctness. Inclusion as a `.cpp` file means symbol visibility and duplication depend on being included once per translation unit. The table is large and unvalidated at compile time, so regression tests are the main guard.

## Test Signals
Known CRC32C vectors, cross-check hardware and software paths, and randomized incremental append tests are the important validation signals after any regeneration.
