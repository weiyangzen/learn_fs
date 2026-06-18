# sources/storage-engines/pebble/metamorphic/build.go

## Purpose
`metamorphic/build.go` builds SST files used by Pebble metamorphic tests for regular ingestion, blob-file ingestion, and external-object ingestion emulation. It translates sorted batch/external iterators into ingestible tables while preserving or transforming point keys, range deletes, range keys, synthetic prefixes, synthetic suffixes, and format-version constraints.

## Important APIs, types, and functions
The central helper is `writeSSTForIngestion`, which writes point keys and spans to an `sstable.Writer`. Public-in-package builders include `buildForIngest`, `buildForIngestWithBlobs`, and `buildForIngestExternalEmulation`. Span helpers are `writeRangeDeletes`, `writeRangeKeys`, `openExternalObj`, and `panicIfErr`.

## Control flow and state behavior
`buildForIngest` creates a temp file path, decides whether value separation and format version allow blob-file ingestion, sorts the batch through `private.BatchSort`, and writes an SST. `writeSSTForIngestion` closes its iterators, skips duplicate user keys or prefixes, zeroes sequence numbers, applies synthetic key transforms, downgrades `DeleteSized` when the target format cannot support it, validates keys, writes raw point records, then writes range deletes and range keys.

`buildForIngestWithBlobs` uses `valsep.SSTBlobWriter`, creates blob files on demand, dispatches point operations by kind, then writes range deletes and range keys through the underlying SST writer. `buildForIngestExternalEmulation` opens a remote/external object, truncates iterators to bounds, optionally inverts synthetic prefixes for reads, and rewrites the object into a local SST for ingest emulation.

State persists as files under the metamorphic test temp directory and possibly external/blob objects. In-memory state includes iterators, writer metadata, blob path lists, and key buffers for duplicate suppression.

## Dependencies and integration points
This code integrates with `pebble.Batch`, `private.BatchSort`, `sstable.Writer`, `valsep.SSTBlobWriter`, `objstorage`, `vfs`, `keyspan`, `rangekey.Coalesce`, format major versions, and metamorphic `Test` state. It is directly tied to writer ingest operations generated elsewhere.

## Risks and test signals
Risks include incorrect iterator closure, duplicate suppression under prefix uniqueness, synthetic suffix handling with range deletes/unsets, format-version downgrades, range key coalescing, and bounds truncation of external objects. Coverage is mostly through metamorphic execution paths rather than isolated unit tests, so failures may surface as generated operation mismatches.
