# sources/storage-engines/rocksdb/table/block_based/uncompression_dict_reader.cc

Purpose: implements an accessor for the compression dictionary block used to decompress table blocks. It abstracts whether the dictionary was prefetched/pinned into the reader or should be read from cache/file on demand.

Important APIs/types/functions: `Create`, `ReadUncompressionDictionary`, `GetOrReadUncompressionDictionary`, `ApproximateMemoryUsage`, and `cache_dictionary_blocks` are implemented here.

Control flow: `Create` optionally reads the dictionary when prefetching or when not using cache, and discards it if cache is enabled but pinning is not requested. `GetOrReadUncompressionDictionary` returns an unowned value when the reader already holds one, otherwise calls the static reader with a cache-use policy derived from table options. The static reader calls `BlockBasedTable::RetrieveBlock` with the table's `compression_dict_handle`.

State and persistence: the dictionary block is persisted in the SST and addressed by `Rep::compression_dict_handle`. In memory, the reader stores a `CachableEntry<DecompressorDict>` that can own, cache-reference, or be empty. Approximate memory includes owned dictionary memory plus object allocation size.

Dependencies/integration: depends on `BlockBasedTable`, `CachableEntry`, `DecompressorDict`, file prefetch buffers, block cache lookup contexts, and logging. Data block reads pass the resulting dictionary/decompressor state into block fetch/decompression code.

Risks and test signals: callers assert the compression dictionary handle is non-null before reading. Error handling logs warnings and returns status, so table open/read paths must decide whether a missing or corrupt dictionary is fatal. This subset lacks direct tests; block fetcher tests exercise decompression but not dictionary-backed compression.
