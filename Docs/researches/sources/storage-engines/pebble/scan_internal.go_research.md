# sources/storage-engines/pebble/scan_internal.go

## Purpose
This file implements Pebble's internal-key scanning machinery for `DB`, `Snapshot`, and eventually-file-only snapshots. It exposes all logical internal state needed by external consumers such as replication or file-only snapshot transfer while optionally skipping lower-level shared or external files and returning ingestable metadata for them.

## Important APIs, Types, and Functions
`ErrInvalidSkipSharedIteration` reports invalid skip-shared or skip-external scans when required lower-level files are not remote/shareable or contain newer keys than the snapshot.

`SharedSSTMeta` captures remote backing, truncated internal bounds, point/range bounds, level, estimated size, and debug table number for a shared SSTable.

`DB.ScanInternal` creates a `scanInternalIterator` with `newInternalIter` and delegates to `scanInternalImpl`.

`newInternalIter` pins read state or version, chooses the read sequence number, initializes blob value fetching, and prepares iterator allocation.

`pointCollapsingIterator` wraps a keyspan interleaving iterator to return at most one point internal key per user key, while still exposing range deletions and hiding points covered by visible range tombstones.

`IteratorLevel` and `IteratorLevelKind` annotate point-key callbacks with memtable, LSM level, and L0 sublevel origin when available.

`truncateSharedFile` and `truncateExternalFile` produce bounded shared/external metadata for skipped files. Shared truncation may open point, range-delete, and range-key iterators to find tight in-range bounds.

`scanInternalImpl` validates options, visits skipped remote files, iterates internal keys, applies rate limiting, and dispatches point, range-delete, range-key, shared-file, and external-file callbacks.

`constructPointIter` builds memtable, L0 sublevel, lower-level, range-delete, and merging iterator stacks while respecting skip levels and blob value fetchers.

`constructRangeKeyIter` builds the internal range-key iterator stack without eliding range key unsets/deletes.

## Control Flow
Initialization pins the read version, trims memtables newer than the scan sequence, copies bounds into owned buffers, constructs point/range-delete iterators, constructs range-key iterators, and then interleaves point and range-key streams.

Skip mode first scans metadata for levels at and below the configured threshold. It verifies remote object metadata, rejects unsupported mixes, ensures file high sequence numbers are visible to the scan snapshot, truncates metadata to `[lower, upper)`, and calls the appropriate visitor. The actual key iterator excludes deeper skipped levels and excludes remote files from the boundary level that are represented through visitors.

Normal key iteration starts at `LowerBound`, calls an optional rate limiter with the current key/value, then dispatches by key kind. Range-key callback keys are copied, zeroed to sequence number 0, sorted by trailer, and passed with span bounds. Range deletions pass start/end/largest sequence. Point keys pass lazy values and origin metadata.

## State and Persistence Behavior
The scanner does not persist new state, but it pins read state/version references, open table iterators, blob readers, range-key iterator pools, and block/cache resources until `Close`. It may read table contents to tighten shared file metadata and estimate remote file size. Blob values for ingested flushables are fetched through a combined blob file mapping.

## Dependencies and Integration Points
The implementation integrates with Pebble read state, versions, memtables, L0 sublevels, manifest levels, objstorage providers, remote/shared storage metadata, external file ingestion metadata, `keyspan` merging/interleaving, `sstable` iterators, blob `ValueFetcher`, block categories, iterator stats, and inflight iterator tracking.

## Risks
Skip-shared and skip-external correctness depends on strict visibility checks and remote object classification. Boundary-level filtering must keep key iteration and visitor metadata mutually consistent. `pointCollapsingIterator` intentionally panics on merges and single deletes and should only be used where those are impossible or handled elsewhere. Shared truncation opens extra iterators and can be expensive. Resource release is complex: read-state refs, version refs, blob fetchers, iterator pools, and range-key states must all be closed even on errors.

## Test Signals
`scan_internal_test.go` covers datadriven internal scans, skip-shared and skip-external visitors, snapshots, eventually-file-only snapshots, file-only snapshot waiting, external ingestion, point collapsing behavior, and scan statistics.
