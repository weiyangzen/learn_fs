# sources/storage-engines/foundationdb/contrib/crc32/crc32_wrapper.c

## Purpose
C wrapper around the PowerPC VPMSUM assembly CRC function. It handles byte-wise alignment, tail processing, initial/final XOR, and exposes a configurable public wrapper symbol.

## Important APIs, Types, And Functions
`crc32_align()` is a static table-driven byte loop, with reflected and non-reflected variants selected by `REFLECT`. `CRC32_FUNCTION_ASM` defaults to `__crc32_vpmsum`. `CRC32_FUNCTION` defaults to `crc32_vpmsum` and calls the assembly for aligned bulk input under `__powerpc64__`.

## Control Flow
For PowerPC64, the wrapper optionally XORs the input CRC, processes small buffers entirely with `crc32_align`, pre-aligns the pointer to 16 bytes, sends the aligned bulk length to assembly, processes the tail with `crc32_align`, and applies final XOR. On non-PowerPC64 builds, the function body compiles but simply returns the input CRC because all real work is guarded.

## State And Persistence
No persistent state. Uses generated `crc_table` from `crc32_constants.h` when `CRC_TABLE` is defined.

## Dependencies And Integration
Included by the `crc32` static library. `crc32c.cpp` references `crc32_vpmsum` through `crc32_wrapper.h` in the PowerPC path.

## Risks
The non-PowerPC return-original behavior is safe only if callers never select this backend there. The pointer parameter is mutable `unsigned char*` even though data is read-only. Correctness depends on the generated constants matching assembly polynomial/reflection settings. Macro customization can silently change exported symbol names.

## Test Signals
PowerPC tests should cover lengths below 31 bytes, unaligned starts, aligned bulk, tail bytes, and nonzero initial CRC. Non-PowerPC builds should verify this object does not become the selected implementation.
