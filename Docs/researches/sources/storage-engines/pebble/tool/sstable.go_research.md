# Research: sources/storage-engines/pebble/tool/sstable.go

## Purpose
`tool/sstable.go` implements the Pebble CLI's `sstable` command family. It provides read-only introspection for table files: checksum verification, block/record layout, properties, record scans, and disk-usage estimates over key ranges.

## Important APIs, Types, And Functions
The central type is `sstableT`, which owns Cobra commands plus shared flags and state: Pebble options, registered comparers and mergers, key/value formatters, scan bounds, prefix filter, row count, verbosity, and optional blob-loading directory. `newSSTable` wires the subcommands `check`, `layout`, `properties`, `scan`, and `space` and registers shared flags.

`newReader` converts a `vfs.File` into an `objstorage.Readable`, applies Pebble reader options, installs comparer/merger registries, and configures cache options with the parsed file number when available. `foreachSstable` walks file or directory arguments and uses `processFiles` to open `.sst` and `.ldb` files.

`runCheck` validates block checksums, checks sorted internal-key order, and tests prefix iteration via `SeekPrefixGE`. `runLayout` prints the table layout, optionally formatting records. `runProperties` emits either raw `sstable.Properties.String()` output or a tabular summary. `runScan` scans point records, raw range deletions, and raw range keys. `runSpace` calls `EstimateDiskUsage`.

## Control Flow
All commands route through `foreachSstable`, so directory traversal, reader creation, property loading, reader closing, and extension filtering are shared. `runScan` has the richest flow: it may first load blob mappings from a manifest directory, creates an iterator with an optional end bound and blob context, seeks to the start key, materializes raw range tombstones into sorted spans, and then merges point records and tombstones into output order. After point/tombstone output, it separately scans raw range keys.

## State And Persistence
The file is read-only with respect to database data. Persistent state is opened through `vfs.FS` and `objstorage`; transient state includes iterator handles, cache handles, loaded blob mappings, copied last-key buffers, and in-memory tombstone spans. When blob loading is requested, external blob files are opened through `blobFileMappings` and closed after the scan.

## Dependencies And Integration Points
This code integrates CLI flag parsing (`spf13/cobra`), Pebble reader configuration, sstable internals, range deletion/keyspan helpers, blob-loading debug context, object storage, cache handles, and `vfs` traversal. It relies on comparer-specific formatters and prefix split functions for correctness of pretty output and prefix-iteration validation.

## Risks And Edge Cases
Prefix filtering uses `bytes.HasPrefix` plus comparer comparisons, and a comment notes this is only known to be kosher for common comparers. Range tombstone filtering has subtle overlap logic around inclusive/exclusive scan bounds. `runScan` uses `os.Exit(1)` in some range-span error paths, which is abrupt for embedded uses. Missing file numbers disable blob loading for non-numeric paths. Iterator close errors are printed rather than returned.

## Test Signals
Coverage comes indirectly through `TestSSTable` datadriven tests and fixture databases. Important signals include checksum failure text, out-of-order key warnings, prefix iteration failures, layout formatting, non-verbose properties summaries, range deletion/range key scan output, count limiting, key/value formatter behavior, and blob handle loading from manifest/blob directories.
