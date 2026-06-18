# sources/sync-backup/casync/src/compressor.h

## Purpose

`compressor.h` declares the unified streaming compression context and operations for xz, gzip, and zstd.

## Important APIs, Types, and Functions

`CompressorOperation` tracks uninitialized, encode, or decode mode. `CompressorContext` stores the operation, selected `CaCompressionType`, and a union of optional library stream structs. `COMPRESSOR_CONTEXT_INIT` initializes a safe empty context. Public functions include support detection, start encode/decode, finish, input assignment, encode/decode streaming, and magic-byte detection. The status enum defines `COMPRESSOR_EOF`, `COMPRESSOR_MORE`, and `COMPRESSOR_GOOD`.

## Control Flow

The header defines a single context lifecycle: initialize, start for a compression type and direction, feed input, drain output with status-driven loops, finish. Callers branch on status enum values rather than library-specific return codes.

## State and Persistence Behavior

The context contains library-owned allocations for zstd streams and library internal state for zlib/lzma. It should be finished before being discarded. Buffer pointers passed through `compressor_input()` remain caller-owned.

## Dependencies and Integration Points

It includes optional compression headers only when build macros are enabled and uses `cacompression.h` for the shared compression enum. Store/archive code can include this header without directly depending on every compression library when disabled.

## Risks and Edge Cases

Because the union fields only exist under compile-time macros, code must guard access through the adapter. Context reuse after `compressor_finish()` is not guaranteed by the interface. The misspelled include guard name is harmless but should not be copied into new code.

## Test Signals

Build matrix tests should cover all combinations of compression library macros. API tests should verify that disabled compressors compile and return unsupported errors through the implementation.
