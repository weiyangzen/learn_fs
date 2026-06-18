# Research: sources/storage-engines/pebble/valsep/value_separation.go

## Purpose
`valsep/value_separation.go` defines the core `ValueSeparation` interface and metadata structures used when compactions or external writers store some values in separate blob files instead of inline SSTable storage.

## Important APIs, Types, And Functions
`ValueSeparationOutputConfig` describes per-output policy: minimum value size, suffix-based separation disablement, and MVCC-garbage-specific minimum size. `ValueSeparation` defines lifecycle methods `SetNextOutputConfig`, `OutputConfig`, `EstimatedFileSize`, `EstimatedReferenceSize`, `Add`, and `FinishOutput`.

`NewBlobFileInfo` describes a newly created blob file, including writer stats, object metadata, and manifest physical metadata. `ValueSeparationMetadata` returns table blob references, reference size, reference depth, and new blob file info. `NeverSeparateValues` implements the interface by always writing values into the SSTable.

## Control Flow
The interface separates per-output configuration from per-KV addition and final metadata collection. `NeverSeparateValues.Add` resolves the KV value and calls `tw.Add`; `FinishOutput` returns empty metadata. This provides a no-op strategy for callers that want uniform plumbing without blob files.

## State And Persistence
`NeverSeparateValues` has no state. Other implementations use the metadata contracts here to persist blob references into table metadata and blob file metadata into manifests. `EstimatedFileSize` and `EstimatedReferenceSize` are transient planning estimates.

## Dependencies And Integration Points
The interface ties together internal keys, manifest blob references, object storage metadata, SSTable raw writers, and blob file stats. It is consumed by compaction output writing and by `SSTBlobWriter`.

## Risks And Edge Cases
Implementations must keep table inline handles, `BlobReferences`, reference depth, and new physical blob metadata consistent. `MinimumMVCCGarbageSize` uses zero to mean all likely garbage values are eligible, but `SetNextOutputConfig` in the stateful implementation also treats zero as "use global default", which callers must understand. `NeverSeparateValues.Add` still resolves lazy values, so value fetch errors propagate.

## Test Signals
Tests should validate no-op behavior, metadata shape, per-output config override semantics, estimated sizes, and correct pass-through of `forceObsolete` and `KVMeta` to raw SSTable writers.
