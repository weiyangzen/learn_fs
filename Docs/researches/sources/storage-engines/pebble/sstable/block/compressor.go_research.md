## sources/storage-engines/pebble/sstable/block/compressor.go

Purpose: Wraps internal compression compressors with Pebble block-kind routing, adaptive compression support, minimum-reduction fallback, input-byte accounting, and compression statistics.

Important APIs/types/functions: `Compressor`, `MakeCompressor`, `maybeAdaptiveCompressor`, `Close`, `Compress`, `UncompressedBlock`, `Stats`, `InputBytes`, `Decompressor` alias, and `GetDecompressor`.

Control flow: Construction creates one compressor for data blocks, one for value/blob value blocks, and one for all other blocks. Adaptive compressors are used when a `CompressionSetting` specifies a cutoff and differs from `OtherBlocks`, sampling every 10 blocks with a 256 KiB half-life and random seed. `Compress` increments per-kind input bytes, compresses with the chosen compressor, rejects compressed output if it fails `MinReductionPercent`, records stats with the actual setting used, and returns the durable `CompressionIndicator`. `Close` closes all underlying compressors and zeros the struct.

State and persistence behavior: `Stats` are in-memory until copied into table properties. `InputBytes` feed logical compression counters on `PhysicalBlockMaker.Close`. The returned compression indicator is persisted in block trailers.

Dependencies and integration points: Depends on `internal/compression`, `blockkind`, and Go `iter`/`math/rand`. Used by `PhysicalBlockMaker` for all logical-to-physical block conversion.

Risks: `Compressor` is not documented as thread-safe and has mutable stats/input counters. `Stats` returns an internal pointer valid only until the next compressor call. The minimum-reduction comparison uses integer math; edge thresholds require care. Using a closed compressor after `Close` will operate on zeroed fields and likely panic.

Test signals: `compressor_test.go` validates block-kind routing for several compression settings. Compression stats tests cover the stats representation.
