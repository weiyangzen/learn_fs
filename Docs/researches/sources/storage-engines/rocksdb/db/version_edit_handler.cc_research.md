# sources/storage-engines/rocksdb/db/version_edit_handler.cc

## Purpose

This file implements MANIFEST replay handlers built around `VersionEdit`. It reads logical records from a MANIFEST log, decodes edits, handles atomic-group buffering, applies edits to column families and version builders, loads table metadata, verifies file availability, maintains replay parameters, supports point-in-time recovery, supports manifest tailing for secondary/follower instances, and provides manifest dump output.

## Important APIs, classes, and functions

- `VersionEditHandlerBase::Iterate` is the generic replay loop over `log::Reader`.
- `ListColumnFamiliesHandler::ApplyVersionEdit` tracks column-family add/drop records to list live CF names.
- `FileChecksumRetriever` builds a file-number to checksum map across SST and blob file additions, removing entries on file deletion or CF drop.
- `VersionEditHandler` implements normal recovery replay into a `VersionSet`, including CF creation/drop, WAL changes, non-CF file edits, global manifest parameters, table loading, and final version installation.
- `VersionEditHandlerPointInTime` extends replay to maintain the latest valid point-in-time version when the end state may reference missing files.
- `ManifestTailer` extends point-in-time handling for secondary/follower catch-up, including repeated reads and mode switching from recovery to catch-up.
- `DumpManifestHandler` prints individual edits and final column-family/version state for diagnostic tools.

## Control flow

`VersionEditHandlerBase::Iterate` initializes the handler, then reads records until the reader reaches `max_manifest_read_size_`, returns EOF, hits a read status error, or a handler status fails. Each record is decoded into a `VersionEdit`, the end offset is stored as `last_valid_record_end_`, and the edit is fed into `AtomicGroupReadBuffer`. Atomic-group edits are only replayed when the buffer is full; non-atomic edits are applied immediately. On corruption, the handler appends the MANIFEST filename to the error state.

Normal `VersionEditHandler::ApplyVersionEdit` dispatches by edit type: column-family add, column-family drop, WAL addition, WAL deletion, or regular CF operation. CF add checks whether the CF is already open or intentionally not opened, handles the persistent stats CF specially, and creates a `ColumnFamilyData` plus `BaseReferencedVersionBuilder` when appropriate. CF drop removes builders and marks the CF dropped. WAL operations update `version_set_->wals_`. Regular CF operations validate CF presence, pad stripped user-defined timestamp file boundaries when needed, and call `MaybeCreateVersionBeforeApplyEdit`.

At end of iteration, `CheckIterationResult` validates required manifest globals: log number, next file number, and last sequence. It rejects unopened column families in normal mode, updates max CF/min log/file-number accounting, checks builder level consistency, loads table handlers unless configured to skip, creates final versions for all live CFs, updates manifest read offsets and valid-record offsets, advances sequence-number atomics, and stores previous log number.

Point-in-time replay wraps builder save points around each edit. It saves a version when a valid state is about to become invalid or when a valid state is explicitly forced. It suppresses table-loading failures caused by missing files and uses atomic update buffering so multi-CF atomic groups only become visible all at once. Manifest tailing reuses recovery initialization for the first pass, then in catch-up mode rebuilds builders from current live versions and tracks changed CFs.

## State and persistence behavior

The handlers transform durable MANIFEST records into live `VersionSet` state. `version_edit_params_` accumulates persistent manifest parameters such as DB ID, log numbers, next file, max CF, min log number to keep, last sequence, and last compacted manifest size. `last_valid_record_end_` records the byte offset after the last fully decoded logical edit, allowing recovery/tailing to distinguish durable valid data from a torn or partial tail.

Column-family state is split among `builders_` for opened CFs and `do_not_open_column_families_` for CFs present in MANIFEST but not requested by the caller. Read-only or tailing modes can tolerate unopened CFs differently from normal DB open. User-defined timestamp state is also persistent: if enabling UDT is detected for a CF, existing SST boundaries are padded and files are marked as not having persisted UDTs so in-memory boundaries match the running comparator.

Point-in-time state is held in `versions_` and `atomic_update_versions_`. Incomplete atomic groups are discarded rather than partially applied. `HasMissingFiles` delegates to version builders so callers can detect best-effort recovery outcomes.

## Dependencies and integration points

This file integrates with `log::Reader`, `AtomicGroupReadBuffer`, `VersionEdit`, `VersionSet`, `ColumnFamilySet`, `ColumnFamilyData`, `BaseReferencedVersionBuilder`, `VersionBuilder`, table cache loading, blob sources/readers, WAL state, persistent stats CF options, user-defined timestamp utilities, `IOTracer`, RocksDB logging, and manifest dump stdout tooling.

## Risks and edge cases

- Atomic-group handling must preserve all-or-nothing visibility. Incomplete or nested groups produce corruption or discarded buffered versions.
- `CheckIterationResult` performs many finalization actions; failures after partial builder state exists must avoid installing invalid versions.
- Missing table files are conditionally tolerated depending on `no_error_if_files_missing_`, `paranoid_checks`, point-in-time mode, and best-effort recovery settings.
- `MaybeHandleFileBoundariesForNewFiles` assumes all new files in one edit have consistent `user_defined_timestamps_persisted` unless existing SSTs are being marked no-UDT. Mixed values are corruption.
- `FileChecksumRetriever::ApplyVersionEdit` returns `NotFound` when deleting an unknown checksum entry, so it is stricter than some recovery paths.
- `ManifestTailer::OnColumnFamilyAdd` ignores new CFs not already present during catch-up, which is intentional but important for secondary/follower semantics.
- Blob verification opens blob files but has a TODO for checksum verification.

## Test signals

The implementation exposes sync points around `Iterate` finish, load-table skipping, and point-in-time version creation. It is exercised by manifest recovery tests, secondary/tailing tests, WAL tracking tests, checksum retrieval tests, dump-manifest tests, and downstream version-builder tests. The explicit corruption strings in this file form part of recovery diagnostics.
