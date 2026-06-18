<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/table.cc

Purpose: Bridges Java table configuration classes to C++ table factory objects for plain and block-based table formats.

Important APIs/types/functions: `PlainTableConfig_newTableFactoryHandle` fills `PlainTableOptions` and returns `NewPlainTableFactory(options)`. `BlockBasedTableConfig_newTableFactoryHandle` fills `BlockBasedTableOptions`, including cache/index/filter settings, checksum/index enum conversions, block sizes, format version, key-value separation settings, compression options, block alignment, index shortening/search type, and optional cache construction.

Control flow: Java passes a long parameter list representing table config fields. C++ maps each primitive/handle to an options struct. Existing `Cache`, `PersistentCache`, and `FilterPolicy` shared pointer handles are dereferenced into options. If no block cache handle is supplied but a non-negative size is, a new LRU cache is created.

State and persistence behavior: The returned table factory configures how RocksDB writes and reads SST tables. It affects persisted SST format/layout but this bridge only creates factory objects.

Dependencies and integration points: Depends on generated table config headers, `rocksdb/table.h`, cache/filter policy headers, conversion helpers, and `portal.h`. The returned factories are consumed by options JNI code.

Risks: The block-based signature is very wide, so Java/C++ parameter ordering must stay exactly synchronized. `super_block_alignment_space_overhead_ratio` is assigned through `static_cast<size_t>` even though its Java name suggests a ratio, which deserves API compatibility review. If no cache handle and negative cache size are supplied, the bridge forces `no_block_cache`. Enum conversion helpers must reject or handle invalid bytes.

Test signals: Tests should inspect options through created DB/table behavior, verify cache handle vs size-created cache paths, filter policy installation, enum mappings, and Java signature regeneration after parameter additions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table.cc -->
