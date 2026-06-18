# sources/storage-engines/pebble/excise_test.go

## Purpose
Provides datadriven coverage for excise behavior across local, remote, shared, flushable, and concurrent scenarios, plus direct tests of tight and loose excised table bounds.

## Important APIs, Types, And Functions
`TestExcise` drives a single DB with commands for building/ingesting SSTables, external ingestion, file-only snapshots, iteration, metrics, dry-run excise, and backing confirmation. `TestConcurrentExcise` coordinates two DBs over shared remote storage and blocked compactions. `TestExciseBounds` builds SSTables and calls `determineLeftTableBounds`, `determineRightTableBounds`, and loose-bound helpers directly.

## Control Flow
The main datadriven harness resets an in-memory FS and remote storage, opens a DB with virtual/flushable ingest excise support, and executes commands from `testdata/excise`. Concurrent tests switch between two DBs, replicate key spans through `ScanInternal` and `IngestAndExcise`, block selected compactions through event callbacks, and wait for errors/unblocks. Bounds tests build raw SSTables, open raw iterators, and print calculated metadata.

## State And Persistence Behavior
Tests create real Pebble manifests, virtual SSTables, remote object catalog state, shared backing files, blob references, eventually file-only snapshots, and flushable ingest metrics. They check persistence across reopen and confirm virtual fragments can share one `TableBacking`.

## Dependencies And Integration Points
Uses testkey comparer, block property collectors, remote in-memory storage, object provider, raw SST writers, keyspan encoders, datadriven helper commands, event listener synchronization, and table stats wait helpers.

## Risks And Edge Cases
Coverage targets range deletions, range keys, masking filters, tiny blocks, remote object movement, memtable flush interaction, EFOS protected ranges, concurrent compaction cancellation, shared-SST replication, inclusive-bound assertions, and loose bounds for remote files.

## Test Signals
Signals include exact iterator output, `get` results, LSM layouts, version edit dry-runs, metrics, table stats completion, compaction error messages, backing equality, and printed tight-versus-loose bounds.
