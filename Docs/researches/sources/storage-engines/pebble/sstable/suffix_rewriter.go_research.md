# sources/storage-engines/pebble/sstable/suffix_rewriter.go

## Purpose
Implements efficient SSTable key-suffix replacement. It can rewrite all point SET keys and range-key SET suffixes from `from` to `to`, preserving the input table format and copying or recomputing selected table metadata.

## Important APIs, Types, And Functions
Top-level APIs are `RewriteKeySuffixesAndReturnFormat`, `RewriteKeySuffixesViaWriter`, and `NewMemReader`. Internal helpers include `rewriteKeySuffixesInBlocks`, `rewriteDataBlocksInParallel`, `rewriteRangeKeyBlockToWriter`, `getShortIDs`, `copyFilterWriter`, `readBlockBuf`, and `memReader`. `blockRewriter` abstracts row- or column-block rewriting, and `blockWithSpan` carries rewritten block span keys plus compressed physical data.

## Control Flow And State
The fast path opens a memory reader, reads properties, validates concurrency, rejects value-block SSTables, requires matching comparer names, forces the output table format to the input format, disables filter rebuilding, and delegates to `RawWriter.rewriteSuffixes`. Data blocks are rewritten in parallel with static round-robin partitioning: each worker reads and verifies a block, calls a block rewriter, validates start/end keys, compresses the rewritten block, and merges compression stats under a mutex. Errors are collected deterministically by worker id.

Range key blocks are rewritten through a raw range-key iterator: every key must be `RangeKeySet`, every suffix must equal `from`, and suffix fields are replaced before re-encoding spans. Existing filters can be copied through `copyFilterWriter` because prefix filters are unaffected by suffix replacement. `RewriteKeySuffixesViaWriter` is slower but simpler: it iterates all keys through a reader, rewrites each key into a new writer, and rederives more metadata.

## Persistence And Integration
The APIs read SSTable bytes from memory and write a new SSTable to `objstorage.Writable`. They integrate with `Reader`, `RawWriter`, `RawRowWriter.rewriteSuffixes`, block property collectors, filters, block compression/checksum code, and in-memory `objstorage.Readable`. The fast path preserves table format and copies filter bytes; properties are partially copied and partially recomputed by the writer.

## Dependencies
Depends on `base.Comparer` splitting and validation, `objstorage`, `block` compression/checksum/decompression, `blockkind`, `invariants`, `sync`, `slices`, `cmp`, unsafe alignment checks, and block property collector contracts such as `SupportsSuffixReplacement` and `AddCollectedWithSuffixReplacement`.

## Risks
Inputs are constrained: all point keys must be SETs with the `from` suffix, range keys must be SETs with the `from` suffix, value-block SSTables are rejected, and range deletes are ignored by the top-level documented contract. Obsolete bits are lost. Copying filter blocks assumes prefix-only filtering and matching comparer/split behavior. `readBlockBuf` may return slices into the source SSTable, so callers must clone when a writable may mutate buffers. Parallel rewriting must preserve output block order and deterministic error reporting.

## Test Signals
`suffix_rewriter_test.go` checks property collector remapping, range-key suffix replacement, filter copying, format preservation, idempotence against mutable output buffers, and equivalence between fast by-block and slower reader/writer rewrites when formats match. `BenchmarkRewriteSST` compares throughput across sizes, compression modes, and concurrency.
