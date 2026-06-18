# sources/storage-engines/rocksdb/table/block_based/uncompression_dict_reader.h

Purpose: declares `UncompressionDictReader`, the table-reader helper that provides access to an SST compression dictionary independent of ownership and cache pinning mode.

Important APIs/types/functions: static `Create`, public `GetOrReadUncompressionDictionary`, `ApproximateMemoryUsage`, private constructor, `cache_dictionary_blocks`, and static `ReadUncompressionDictionary`. The class stores the owning table pointer and a `CachableEntry<DecompressorDict>`.

Control flow: the class supports eager creation with optional prefetch/pin and lazy retrieval for later block reads. The static read routine centralizes the actual `RetrieveBlock` call so both creation and lazy reads follow the same path.

State and persistence: persisted state is only the dictionary block bytes in the SST. Runtime state is the cached/owned dictionary entry and the borrowed table pointer. The reader does not mutate table metadata.

Dependencies/integration: includes `cachable_entry.h` and `format.h`; forward-declares table, prefetch, get context, lookup context, and read options. It is integrated into block-based table open/read plumbing when compression dictionary handles are present.

Risks and test signals: the table pointer must outlive the reader. Cache behavior follows `cache_index_and_filter_blocks`, which can surprise callers because dictionaries are metadata-like but used for data decompression. There are no direct tests in this subset.
