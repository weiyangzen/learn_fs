# sources/storage-engines/rocksdb/db/version_edit_handler.h

## Purpose

This header declares the MANIFEST replay handler hierarchy for RocksDB version edits. It defines the base iteration interface, specialized handlers for listing column families and retrieving checksums, the main `VersionEditHandler` used during DB recovery, point-in-time recovery support, manifest tailing for secondary/follower instances, and a dump handler for diagnostic output.

## Important APIs and types

- `VersionEditHandlerBase` owns replay status, read options, `AtomicGroupReadBuffer`, `last_valid_record_end_`, and the `Iterate` entry point. Subclasses implement `ApplyVersionEdit` and can hook initialization, atomic-group begin/end, and final iteration checks.
- `ListColumnFamiliesHandler` maintains a map from CF ID to name, initialized with the default CF, and applies only CF add/drop edits.
- `FileChecksumRetriever` scans edits up to a bounded manifest size and exposes `FetchFileChecksumList`.
- `VersionEditHandler` is the normal recovery handler. It owns requested column-family descriptors, a `VersionSet`, per-CF version builders, unopened-CF tracking, replayed version parameters, missing-file behavior flags, IO tracing, table-load skipping, UDT boundary state, and epoch-number requirements.
- `VersionEditHandlerPointInTime` adds maps of saved `Version*` objects and atomic-update buffers so recovery can retain the most recent valid version when later manifest edits point at missing files.
- `ManifestTailer` adds recovery/catch-up mode, changed-CF tracking, new-manifest preparation, and intermediate-file collection.
- `DumpManifestHandler` wraps normal replay while printing each edit and final CF/version state.

## Control flow and extension points

Users create a concrete handler, pass it a MANIFEST `log::Reader` via `Iterate`, then inspect `status()` and handler-specific results. `VersionEditHandler` subclasses customize behavior by overriding `VerifyFile`, `VerifyBlobFile`, `OnColumnFamilyAdd`, `MaybeCreateVersionBeforeApplyEdit`, `LoadTables`, `MustOpenAllColumnFamilies`, or `CheckIterationResult`.

The normal handler's protected methods break replay into clear phases: initialize the default CF, classify CF IDs, create/drop CFs, handle WAL changes, handle non-CF edits, apply version edits through builders, load tables, extract replay parameters, and adjust UDT file boundaries. Point-in-time subclasses override the version-creation and table-loading pieces to save valid intermediate states instead of requiring the final manifest state to be complete.

## State and persistence behavior

The header exposes recovery state that mirrors durable MANIFEST content. `VersionEditParams` tracks replayed DB-wide manifest values. `builders_` hold per-CF edit accumulation. `do_not_open_column_families_` records manifest CFs omitted from the caller's open list. `last_valid_record_end_` is the persistence boundary for fully decoded records. For best-effort and tailing modes, `versions_` stores candidate recoverable versions and `atomic_update_versions_` delays visibility until all affected CFs have valid versions.

The flags `track_found_and_missing_files_`, `no_error_if_files_missing_`, `skip_load_table_files_`, `allow_incomplete_valid_version_`, and `epoch_number_requirement_` make the same replay machinery usable for normal open, read-only open, best-effort recovery, manifest dump, file checksum retrieval, and secondary catch-up.

## Dependencies and integration points

The declarations depend on `version_builder.h`, `version_edit.h`, `version_set.h`, `ColumnFamilyDescriptor`, `ColumnFamilyData`, `Version`, `VersionBuilder`, `FileChecksumList`, `IOTracer`, `ReadOptions`, and blob metadata types. These handlers are integration points between manifest log reading and the rest of DB recovery, including table-cache loading, blob-file verification, WAL lifecycle tracking, and diagnostic tooling.

## Risks and edge cases

- The classes are explicitly not thread-safe when shared; external synchronization is required.
- Subclass contracts are subtle: overriding `LoadTables`, `MaybeCreateVersionBeforeApplyEdit`, or `MustOpenAllColumnFamilies` changes recovery semantics significantly.
- Point-in-time recovery owns raw `Version*` pointers in maps and must delete or append them exactly once.
- Atomic update buffering assumes CF additions/drops inside an atomic group are unsupported and should become corruption.
- `ManifestTailer::PrepareToReadNewManifest` resets initialization and atomic read buffering; callers must use it before switching manifest files.
- `DumpManifestHandler` can print debug strings containing non-terminating null characters, so it writes with `fwrite` rather than C-string APIs.

## Test signals

The header declares testable behaviors through virtual methods and mode-specific APIs: `GetLastValidRecordEnd`, `HasMissingFiles`, `GetUpdatedColumnFamilies`, `GetAndClearIntermediateFiles`, and dump output. Implementation tests should cover normal recovery, read-only/unopened CF handling, missing-file tolerance, atomic groups, tailing mode transitions, checksum retrieval, and dump output.
