# sources/storage-engines/rocksdb/util/simple_mixed_compressor.cc

## Purpose

Implements experimental mixed-compression wrappers that can compress different SST blocks with different built-in compression algorithms. `RandomMixedCompressor` picks an algorithm randomly per block, while `RoundRobinCompressor` cycles through algorithms globally.

## APIs, control flow, and state

`MultiCompressorWrapper` builds a vector of built-in compressors from `GetSupportedCompressions()`, skipping `kNoCompression`. Dictionary guidance, serialized dictionary, preferred type, working area, and dictionary-specialized cloning currently delegate to the last compressor in the vector. `RandomMixedCompressor::CompressBlock` chooses a vector index using thread-local `Random`; `RoundRobinCompressor::CompressBlock` increments static `block_counter` and takes modulo compressor count. Both forward the actual compression call and output compression type to the selected compressor. The managers ignore the requested preferred type and return the wrapper compressor for an SST.

## Dependencies and integration

This code integrates with RocksDB's advanced compression API, `CompressionManagerWrapper`, `Compressor`, `CompressionOptions`, and option helper functions. It also uses `util/random.h` and `RelaxedAtomic`. SST block readers rely on `out_compression_type`, so mixed algorithms are viable only when each block stores its type correctly.

## Risks and test signals

No direct tests are present here. Risks include an empty `compressors_` vector if no non-null built-in compressor is available, weak dictionary support because specialization falls back to a single compressor, and global round-robin state crossing SSTs/tests. Manager behavior ignores `preferred`, which is intentional for testing but surprising in production-style configuration.
