# sources/storage-engines/pebble/internal/manifest/blob_metadata.go

## Purpose
This file defines manifest metadata and live-state tracking for Pebble blob value files. It bridges stable blob file IDs referenced by sstables, physical blob files on disk, version reference counts, lookup mappings, aggregate statistics, and rewrite-candidate selection for space reclamation.

## Important APIs, Types, And Functions
`BlobReference` records a table's reference to a blob file ID, value sizes, and estimated physical size. `MakeBlobReference` validates and computes that estimate. `BlobFileMetadata` maps stable `FileID` to a reference-counted `PhysicalBlobFile`. `PhysicalBlobFile` stores file number, size, value size, creation time, refs, and optional blob properties. `BlobReferences` implements `sstable.BlobReferences`. `BlobFileSet` is a copy-on-write B-tree keyed by blob file ID with `All`, `Count`, `Lookup`, `LookupPhysical`, `clone`, `insert`, `remove`, and `release`. `CurrentBlobFileSet` tracks blob files and references in the latest version, with `Init`, `ApplyAndUpdateVersionEdit`, `Stats`, `Metadatas`, `ReplacementCandidate`, and `ReferencingTables`. Heap helpers rank rewrite candidates by live-data ratio or creation time.

## Control Flow
Blob reference construction validates non-zero and bounded value sizes in invariant builds. Physical files increment/decrement atomic refs as versions and table metadata are retained or released; refcount zero adds the file to obsolete files. `BlobFileSet.LookupPhysical` manually inlines B-tree search for read-path performance. `CurrentBlobFileSet.Init` loads blob files from a `BulkVersionEdit`, walks extant table references, computes aggregate stats, and places partially unreferenced files into either a recently-created heap or rewrite-candidate heap. `ApplyAndUpdateVersionEdit` updates the current set for new blob files, replacement blob files, new table references, deleted table references, obsolete blob-file deletions, heap membership, and aged-file promotion.

## State, Persistence, And Side Effects
Manifest persistence is represented by version edits containing blob-file additions/deletions and table blob references; this file itself mostly manages derived in-memory state. `PhysicalBlobFile.refs` and `propsValid` are atomic mutable fields. `BlobFileSet` is version-scoped copy-on-write state that preserves old versions. `CurrentBlobFileSet` is latest-version mutable state protected by the version set log lock and is explicitly not thread-safe. `ApplyAndUpdateVersionEdit` mutates the input `VersionEdit` by adding `DeletedBlobFiles` when references disappear.

## Dependencies And Integration Points
Dependencies include `container/heap`, generic iterators, maps/slices, atomics, time, CockroachDB errors/redaction, Pebble `base`, `humanize`, `invariants`, `strparse`, `sstable`, and `sstable/blob`. Integration points include manifest version edit encode/decode, `BulkVersionEdit`, table metadata blob references, obsolete-file collection, read-path blob lookup through `base.BlobFileMapping`, and compaction scheduling for blob rewrite candidates.

## Risks And Edge Cases
Reference accounting is the core risk: table moves in the same version edit must decrement temporary double-counting without deleting references, and deleted tables must use the same `*TableMetadata` identity recorded in `currentBlobFile.references`. Virtual sstables without `BackingValueSize` make rewrite eligibility unsafe and are tracked separately. Replacement blob files must be paired with a matching deleted physical file entry. Heap indexes must remain synchronized through push/remove/fix operations. `MakeBlobReference` can overflow `valueSize * phys.Size` for extreme values. Debug parsers are test-only and intentionally parse string formats rather than persisted binary records.

## Test Signals
`blob_metadata_test.go` covers debug parse round trips, datadriven `CurrentBlobFileSet` behavior, lookup correctness over 10,000 blob files, and lookup benchmarking. Broader manifest tests outside this subset cover version edit persistence and blob file invariants.
