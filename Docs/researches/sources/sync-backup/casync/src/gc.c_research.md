# sources/sync-backup/casync/src/gc.c

## Purpose

`gc.c` implements garbage collection support for casync stores. It builds a collection of chunk IDs referenced by index files and removes chunk files from a store that are not in that collection.

## Important APIs, Types, and Functions

`struct CaChunkCollection` stores `n_used`, the number of chunk references seen across indexes, and `used_chunks`, a `Set` of unique `CaChunkID` copies. `chunk_hash_ops` hashes and compares `CaChunkID` values by content with siphash and `memcmp`.

`ca_chunk_collection_new()` allocates the collection and creates the set. `ca_chunk_collection_unref()` frees the set and stored IDs. `ca_chunk_collection_usage()` returns total references added, including duplicates. `ca_chunk_collection_size()` returns unique chunk count. `gc_add_chunk_id()` duplicates an ID, increments usage, and inserts it into the set, treating `-EEXIST` as success after `set_consume()` frees duplicates.

`ca_chunk_collection_add_index()` opens a `CaIndex` for a path and reads chunk IDs until EOF, adding each to the collection. `ca_gc_cleanup_unused()` iterates a `CaStore`, parses chunk IDs from chunk filenames before the dot, skips IDs in `used_chunks`, and removes unused chunk files and empty subdirectories unless dry-run is set. Verbose mode prints actions or summary.

## Control Flow

The typical flow is create collection, add one or more index files, optionally inspect usage/size, then pass the collection and a store to cleanup. Cleanup loops through the store iterator, parses each chunk filename, checks membership, prints if requested, unlinks unused chunks, tries to remove the containing subdirectory, counts removed chunks/directories, and prints summary for dry-run or verbose mode.

## State and Persistence Behavior

The collection is in-memory. `ca_gc_cleanup_unused()` mutates the store on disk by unlinking unused chunk files and possibly removing now-empty subdirectories. Dry-run mode avoids mutation. The code allocates a reusable `ids` buffer for filename parsing.

## Dependencies and Integration Points

It depends on `CaIndex` for reading index references, `CaStore` and `CaStoreIterator` for walking chunk files, `Set`/hashmap infrastructure for membership, `CaChunkID` parsing/formatting, and Linux `unlinkat()` flags. `gc.h` exposes flags and lifecycle.

## Risks and Edge Cases

There is an odd fragment in `ca_chunk_collection_add_index()`: after `r = ca_index_read_chunk(...)`, it has `if (r < 0)` followed immediately by `assert_se(r >= 0);`. This means negative read errors trigger an assertion before the later error handling, which is likely unintended and can abort instead of returning a logged error. Cleanup assumes chunk filenames contain a dot due to store iterator filtering and asserts that condition. Parse failures are logged and ignored, leaving the file untouched. Directory removal errors are ignored, which is fine for non-empty dirs but can hide permission issues.

## Test Signals

Tests should cover duplicate chunks across indexes, missing/bad index paths, index read error handling, dry-run no mutation, verbose output, malformed chunk filenames, unused chunk deletion, used chunk preservation, empty subdir removal, permission-denied unlink behavior, and collection usage versus unique size counts.
