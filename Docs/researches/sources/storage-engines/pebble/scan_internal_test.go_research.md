# sources/storage-engines/pebble/scan_internal_test.go

## Purpose
This file provides datadriven tests for `ScanInternal`, `ScanStatistics`, skip-shared/external scanning, snapshot variants, and the point-collapsing iterator.

## Important APIs, Types, and Functions
`TestScanStatistics` drives DB setup, batches, snapshots, compactions, flushes, commits, and `ScanStatistics` output over selected levels and key kinds.

`TestScanInternal` drives DB definition/reset, snapshots, eventually-file-only snapshots, batches, ingest, external ingest, compaction, flush, LSM display, and `scan-internal` callbacks.

The local `writeSST` helper writes point, range deletion, and range key data into SSTables for ingest paths.

`TestPointCollapsingIter` constructs fake point keys and range-deletion spans from datadriven input and runs common internal iterator commands against `pointCollapsingIterator`.

## Control Flow
Datadriven commands maintain maps of named batches, snapshots, and file-only snapshots. `scan-internal` selects a reader (`DB`, `Snapshot`, or EFOS), parses lower/upper bounds and skip flags, installs visitors that print points, range deletions, range keys, shared files, and external files, and calls `ScanInternal`.

External ingest builds an SST into remote in-memory storage, constructs an `ExternalFile` with encoded bounds, and ingests it through `IngestExternalFiles`.

## State and Persistence Behavior
Tests use in-memory local and remote storage. Named batches and snapshots are explicitly closed during cleanup. File-only snapshots can wait for transition before scanning. Remote storage is configured through `remote.MakeSimpleFactory`, `CreateOnSharedAll`, and external-storage locators.

## Dependencies and Integration Points
The tests touch Pebble DB options, object storage providers, remote storage, bloom filters, sstable raw writing, range-key spans, batch sorting, datadriven commands, snapshot APIs, and test comparers.

## Risks
The test harness intentionally covers many codepaths, so output changes can reflect small iterator ordering changes, metadata truncation changes, or remote storage classification changes. It relies on format versions that support shared objects, virtual SSTables, and external files.

## Test Signals
Signals include printed internal keys and values, shared-file metadata bounds, external-file metadata, scan statistics counts and snapshot-pinned keys, LSM output after compactions, and iterator traces for point collapse around range tombstones.
