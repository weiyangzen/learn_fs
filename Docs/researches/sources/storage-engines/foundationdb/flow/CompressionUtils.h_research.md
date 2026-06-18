# sources/storage-engines/foundationdb/flow/CompressionUtils.h

## Purpose
`CompressionUtils.h` declares Flow's compression filter enum and utility API for compressing and decompressing `StringRef` data into an `Arena`.

## Important APIs, Types, and Functions
`CompressionFilter` contains `NONE`, `ZSTD`, and sentinel `LAST`. `CompressionUtils` declares overloads for compression with default or explicit level, decompression, default-level lookup, random filter selection, string conversion helpers, support checking, and the static `supportedFilters` set.

## Control Flow
Inline helpers convert exact strings `"NONE"` and `"ZSTD"` to enum values and back. Unsupported filters throw `not_implemented`. `checkFilterSupported` checks the runtime compiled support set before implementation functions perform work.

## State and Persistence Behavior
The header declares no mutable instance state. Compression outputs are specified as `StringRef` values backed by a caller-provided `Arena`, so persistence depends on the arena owner.

## Dependencies and Integration Points
It includes `flow/Arena.h` and `<unordered_set>`. The implementation is in `CompressionUtils.cpp`, and build support for ZSTD is controlled in the Flow CMake file.

## Risks and Edge Cases
The enum-to-string and string-to-enum helpers must be updated whenever new filters are added before `LAST`. The closing include guard comment has a spelling mismatch, but the macro itself is consistent.

## Test Signals
Tests live in `CompressionUtils.cpp`; compile-time use of this header catches missing enum support and signature drift.
