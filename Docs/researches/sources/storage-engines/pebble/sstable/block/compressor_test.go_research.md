## sources/storage-engines/pebble/sstable/block/compressor_test.go

Purpose: Verifies that `Compressor` chooses the compression setting dictated by a profile for each block kind.

Important APIs/types/functions: `TestCompressor` constructs random `CompressionProfile`s, then calls `MakeCompressor`, `Compress`, `compressionIndicatorFromAlgorithm`, and `Close`.

Control flow: Across 100 runs, the test randomly assigns settings to `DataBlocks`, `ValueBlocks`, and `OtherBlocks` with `MinReductionPercent=0`. It compresses a zeroed 1 KiB source as SSTable data, SSTable value, blob value, SSTable index, and metadata. Returned indicators must match data, value, value, other, and other settings respectively.

State and persistence behavior: Tests transient compressor state only. It indirectly protects durable trailer indicator selection.

Dependencies and integration points: Uses `internal/compression`, `blockkind`, `math/rand/v2`, and `require`.

Risks: It disables minimum-reduction fallback, so fallback-to-none behavior is not covered. It also uses simple zero input and non-adaptive profiles, so adaptive compressor behavior is only indirectly covered elsewhere.

Test signals: Strong signal for `ByKind.ForKind` routing and compression indicator conversion.
