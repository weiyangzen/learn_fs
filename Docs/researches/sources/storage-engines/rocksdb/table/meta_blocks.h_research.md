<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/meta_blocks.h -->
# sources/storage-engines/rocksdb/table/meta_blocks.h

Purpose: Declares table meta block names, builders, collector notification helpers, property parsing, and file-level meta block read/find APIs shared by RocksDB table builders and readers.

Important APIs and types: Exposes `MetaIndexBuilder`, `PropertyBlockBuilder`, `LogPropertiesCollectionError`, collector notification helpers, `ParsePropertiesBlock`, `ReadTablePropertiesHelper`, `ReadTableProperties`, `FindOptionalMetaBlock`, `FindMetaBlock`, `FindMetaBlockInFile`, `ReadMetaIndexBlockInFile`, and `ReadMetaBlock`. External block-name constants identify properties, index, compression dictionary, and range deletion meta blocks.

Control flow: Table builders add meta block handles and properties through builder classes, then call `Finish()` to produce block contents. Readers use footer/metaindex helpers to find a named block, with optional and required variants differing only in missing-block status behavior. Property readers return a heap-allocated `TableProperties` only on success.

State and persistence: The declarations define the API for SST-persistent metadata and table properties, but the header itself owns no runtime state beyond builder member declarations. Builders keep sorted maps and block builders until finish.

Dependencies and integration points: Depends on table format primitives (`BlockHandle`, `Footer`, `BlockContents`), block-based builders, table property collectors, `RandomAccessFileReader`, `FilePrefetchBuffer`, immutable/read options, and optional memory allocator support.

Risks: Callers must pass the correct table magic number and file size for footer parsing. Ownership of returned `TableProperties` is through `unique_ptr`, and output pointers are modified only on success. Misusing `ReadMetaBlock` for properties bypasses checksum compatibility logic.

Test signals: Compile coverage across block-based and plain table builders/readers, metaindex construction, properties reading with and without custom allocator, optional missing-block lookup, and required missing-block corruption behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/meta_blocks.h -->
