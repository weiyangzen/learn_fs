<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/meta_blocks.cc -->
# sources/storage-engines/rocksdb/table/meta_blocks.cc

Purpose: Implements construction, lookup, parsing, and reading of SST meta blocks, especially the metaindex block and table properties block. It also dispatches table property collector callbacks during table building.

Important APIs and functions: Defines meta block names `kPropertiesBlockName`, `kIndexBlockName`, `kCompressionDictBlockName`, and `kRangeDelBlockName`. Implements `MetaIndexBuilder`, `PropertyBlockBuilder`, `LogPropertiesCollectionError`, `NotifyCollectTableCollectorsOnAdd`, `NotifyCollectTableCollectorsOnBlockAdd`, `NotifyCollectTableCollectorsOnFinish`, `ParsePropertiesBlock`, `ReadTablePropertiesHelper`, `ReadTableProperties`, `FindOptionalMetaBlock`, `FindMetaBlock`, `ReadMetaIndexBlockInFile`, `FindMetaBlockInFile`, and `ReadMetaBlock`.

Control flow: Builders collect properties/handles into sorted `KVMap`s and emit block-builder output. Property parsing iterates the properties block in sorted order, rejects unsorted duplicates, decodes known uint64 properties, copies known string properties, preserves legacy deleted/merge counters in user properties, and stores unknown keys as user-collected properties. Meta reads load the footer, fetch the metaindex block with `BlockFetcher`, seek the desired meta block handle, then fetch the target block. Table properties have special checksum handling: read once without checksum, parse global sequence offset, verify checksum, optionally zero the external SST global seqno for compatibility, and retry through filesystem reconstruction on corruption.

State and persistence: The code writes persistent SST metadata: properties, metaindex entries, optional index/dictionary/range-deletion block handles, DB/session/host IDs, timestamps, compression stats, and user-collected properties. Runtime state is limited to local builders, block handles, block contents, and temporary parsed `TableProperties`.

Dependencies and integration points: Uses block-based `BlockBuilder`, `Block`, `BlockFetcher`, footer parsing, `RandomAccessFileReader`, `FilePrefetchBuffer`, table properties collectors, persistent cache options, filesystem verify-and-reconstruct support, stats ticks, and logging. Table builders call the collector notification functions and readers call the meta block find/read helpers.

Risks: Properties must remain strictly sorted and unique. Malformed varints are logged and skipped rather than failing the whole parse. External SST global seqno mutation makes checksum verification nontrivial. Meta blocks are assumed uncompressed. The helper asserts that `ReadMetaBlock` is not used for properties because properties need special checksum handling.

Test signals: Cover property block round trips, unsorted/duplicate property corruption, malformed property values, external SST global sequence checksum compatibility, filesystem corruption retry counters, missing optional vs required meta blocks, footer read failures, prefetch-buffer paths, and user-defined property collector error logging.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/meta_blocks.cc -->
