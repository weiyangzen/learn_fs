# sources/storage-engines/rocksdb/util/simple_mixed_compressor.h

## Purpose

Declares the mixed compressor wrappers and managers used to exercise SST files whose blocks are compressed with multiple algorithms.

## APIs, control flow, and state

`MultiCompressorWrapper` extends `Compressor` and owns `CompressionOptions` plus a vector of concrete compressor instances. It exposes dictionary/working-area hooks and specialized cloning. `RandomMixedCompressor` and `RoundRobinCompressor` override `Name`, `Clone`, and `CompressBlock`; `RoundRobinCompressor` also declares the static atomic `block_counter`. `RandomMixedCompressionManager` and `RoundRobinManager` override `Name` and `GetCompressorForSST`.

## Dependencies and integration

The header depends on `rocksdb/advanced_compression.h` and `util/atomic.h`. Integration is via compression-manager configuration rather than table-reader logic; once selected, the compressor returns per-block compression types consumed by normal SST encoding.

## Risks and test signals

The public declarations make no ownership transfer for outside code except through `unique_ptr<Compressor>` returns. There are no local unit tests. The key design risk is that dictionary-oriented methods are declared on the multi-wrapper but are not truly per-algorithm aware in the implementation.
