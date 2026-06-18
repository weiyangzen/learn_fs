# sources/storage-engines/foundationdb/flow/CompressionUtils.cpp

## Purpose
`CompressionUtils.cpp` implements Flow compression helpers for `CompressionFilter::NONE` and optionally `CompressionFilter::ZSTD`, including support discovery, default compression levels, random filter selection, and unit tests.

## Important APIs, Types, and Functions
The implemented methods are `CompressionUtils::compress(filter, data, arena)`, `compress(filter, data, level, arena)`, `decompress`, `getDefaultCompressionLevel`, `getRandomFilter`, and the static `supportedFilters`. Test helpers `testCompression` and `testCompression2` validate round trips and compressibility.

## Control Flow
At static initialization, `getSupportedFilters` adds `NONE` and, when `ZSTD_LIB_SUPPORTED` is defined, `ZSTD`. All public operations call `checkFilterSupported`. `NONE` copies bytes into the provided arena. `ZSTD` uses `ZSTD_compressBound`, `ZSTD_compress`, `ZSTD_decompressBound`, and `ZSTD_decompress`, then copies the result into the arena. Errors become `internal_error`.

## State and Persistence Behavior
No durable state exists. The only global state is the supported filter set. Returned compressed or decompressed data is arena-owned, so caller arena lifetime controls validity.

## Dependencies and Integration Points
The file depends on `CompressionUtils.h`, `Arena`, Flow errors, deterministic randomness, unit tests, and optionally libzstd. `flow/CMakeLists.txt` enables `ZSTD_LIB_SUPPORTED` when `FLOW_USE_ZSTD` is on.

## Risks and Edge Cases
`ZSTD_decompressBound` can return an unknown or very large bound for malformed data, so callers should not feed untrusted arbitrary compressed payloads without considering allocation size. `testCompression` asserts compressed random data differs from input; with `NONE` that would be false, so that helper is only used for ZSTD.

## Test Signals
Tests cover no-compression round trip and, when compiled with zstd, random-data zstd round trip plus a highly compressible string size check. Trace events mark completion.
