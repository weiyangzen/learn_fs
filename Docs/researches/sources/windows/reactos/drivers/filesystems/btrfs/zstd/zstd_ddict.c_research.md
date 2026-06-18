# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_ddict.c

## Summary
Implements `ZSTD_DDict`, the pre-digested decompression dictionary object, including dictionary ownership, entropy loading, static initialization, and copying dictionary parameters into decompression contexts.

## Key APIs
- Accessors: `ZSTD_DDict_dictContent()`, `ZSTD_DDict_dictSize()`.
- Context transfer: `ZSTD_copyDDictParameters()`.
- Creation: `ZSTD_createDDict_advanced()`, `ZSTD_createDDict()`, `ZSTD_createDDict_byReference()`, `ZSTD_initStaticDDict()`.
- Cleanup/introspection: `ZSTD_freeDDict()`, `ZSTD_estimateDDictSize()`, `ZSTD_sizeof_DDict()`, `ZSTD_getDictID_fromDDict()`.

## Important Behavior
A `ZSTD_DDict` may either copy dictionary bytes into an internal buffer or reference caller-owned memory. Full zstd dictionaries are detected by `ZSTD_MAGIC_DICTIONARY`; their dictionary ID and decompression entropy tables are parsed with `ZSTD_loadDEntropy()`. Raw-content dictionaries are accepted without entropy.

When copied into a `ZSTD_DCtx`, an entropy-bearing DDict installs Huffman and FSE table pointers, repcodes, dictionary prefix bounds, dictionary ID, and entropy-present flags. Static DDict initialization requires an 8-byte-aligned caller buffer and stores any copied dictionary content immediately after the `ZSTD_DDict` object.

## Risks
By-reference dictionaries must outlive the DDict and any decompression using it. `ZSTD_createDDict_advanced()` returns `NULL` for allocator mismatch, allocation failure, or dictionary parse failure, losing the exact zstd error at that API boundary.
