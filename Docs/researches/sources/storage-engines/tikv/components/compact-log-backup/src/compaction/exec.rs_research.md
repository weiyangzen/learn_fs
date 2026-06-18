# sources/storage-engines/tikv/components/compact-log-backup/src/compaction/exec.rs

## Purpose
Executes one `Subcompaction`: loads input log records, sorts and deduplicates them, writes an in-memory SST, uploads the SST artifact, and returns metadata and statistics.

## APIs and control flow
`SubcompactionExecArg` constructs `SubcompactionExec` with output storage, optional Rocks engine, optional output prefix, and optional physical-file cache. `SubcompactExt` controls load concurrency and SST compression. `run` initializes expected checksum/key/size totals from inputs, loads records concurrently, sorts and dedups via `process_input`, adjusts checksum diff for removed duplicates, writes an SST under `out_prefix/outputs`, uploads it with SHA-256, and returns `SubcompactionResult`.

Conflict resolution is intentionally narrow. Identical records dedup. Different records in non-write CF panic. Write-CF conflicts are resolved only for collapsed rollback versus put, or protected rollback precedence; otherwise execution panics. `write_sst` decodes encoded keys to raw start/end metadata, makes end key exclusive by appending `0`, writes data-key-prefixed entries, and records CRC64, versions, sizes, and counts.

## State, dependencies, and integration
Mutable state includes `Source`, external output storage, cooperative yielding, output prefix, optional DB, and load/compact statistics. It depends on Rocks SST traits, external storage, `Sha256Reader`, TiKV key/transaction codecs, retry utilities, metrics, and `PhysicalFileCache`. Its output metadata is consumed by compaction metadata migration writers and checkpoint hooks.

## Risks and test signals
Empty compactions return no SST metadata. Conflict handling can panic on unexpected duplicated values. Output names use UUIDs and timestamp ranges, so uploads are persistent external side effects. Tests compact one or many files, deduplicate duplicates, preserve region hints, verify range elision, fail checksum under failpoints, and exercise write-CF conflict-resolution rules and panic paths.
