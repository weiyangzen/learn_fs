# sources/object-store/minio/cmd/storage-datatypes.go

## Purpose

`storage-datatypes.go` defines message-pack-serializable data structures and small helpers used by MinIO's storage layer and storage REST/grid APIs. The types describe disk information, volume and file metadata, object version metadata, bulk read/write/delete/rename request parameters, and low-level storage responses. The file also includes `go:generate msgp` annotations, so field shape and ordering are part of the internode compatibility contract.

## Important APIs, types, and functions

- Option structs: `BaseOptions`, `DeleteOptions`, `RenameOptions`, `DiskInfoOptions`, and `UpdateMetadataOpts`.
- Disk and metric structs: `DiskInfo` and `DiskMetrics`.
- Volume/listing structs: `VolsInfo`, `VolInfo`, and `FilesInfo`.
- Object metadata structs: `FileInfoVersions`, `RawFileInfo`, and `FileInfo`.
- `FileInfoVersions.Size` sums all version sizes, and `findVersionIndex` resolves normal and `nullVersionID` versions.
- `FileInfo` helpers include `shardSize`, `ShardFileSize`, `ShallowCopy`, `WriteQuorum`, `ReadQuorum`, `Equals`, `GetDataDir`, `IsCompressed`, `InlineData`, `SetInlineData`, and `newFileInfo`.
- Request/response structs include `ReadMultipleReq`, `ReadMultipleResp`, `DeleteVersionHandlerParams`, `MetadataHandlerParams`, `CheckPartsHandlerParams`, `DeleteFileHandlerParams`, `RenameDataHandlerParams`, `RenameDataInlineHandlerParams`, `RenameFileHandlerParams`, `RenamePartHandlerParams`, `ReadAllHandlerParams`, `WriteAllHandlerParams`, `RenameDataResp`, `CheckPartsResp`, `LocalDiskIDs`, `ListDirResult`, `ReadPartsReq`, `ReadPartsResp`, `DeleteBulkReq`, and `DeleteVersionsErrsResp`.
- `newRenameDataInlineHandlerParams` and `Recycle` manage a reusable inline data buffer for rename operations.

## Control flow

Most of the file is declarative. `FileInfoVersions.Size` iterates version entries and sums `Size`. `findVersionIndex` returns `-1` for nil receivers, empty IDs, missing versions, or missing null versions; `nullVersionID` matches entries whose `VersionID` is empty. `ShardFileSize` handles special zero and unknown-length values, then computes erasure shard size for full blocks plus the final partial block. `WriteQuorum` and `ReadQuorum` return delete quorum for delete markers, otherwise data-block quorum with an extra write quorum when data and parity blocks are equal.

`FileInfo.Equals` compares encryption type, compression state, transition info, modification time, and erasure layout. `GetDataDir` normalizes delete markers and legacy XLv1 objects. Inline data helpers use reserved internal metadata keys and suppress inline status for remote/tiered objects. `newFileInfo` initializes erasure algorithm, data/parity counts, block size, and hash distribution for a new object.

`newRenameDataInlineHandlerParams` obtains a byte buffer from `grid.GetByteBufferCap` and embeds it in `FileInfo.Data` so inline data can travel with rename parameters. `Recycle` returns large enough buffers to the grid pool and clears `FI.Data`.

## State and persistence behavior

These structs are serialized across internode storage APIs and persisted in object metadata such as `xl.meta`. Comments repeatedly warn that adding or deleting fields is incompatible and may require bumping internode storage REST versions. `msg` tags encode compact wire names; `msgp:tuple` annotations make selected structs positional, increasing compatibility risk if fields are reordered.

`FileInfo` carries persistent object-version state: bucket volume, object name, version ID, latest/delete markers, transition status and remote-tier identity, data directory, XLv1 flag, modification time, size, mode, writer version, user/internal metadata, part list, erasure layout, replication state, optional inline data, version counts, successor time, write freshness, delete index, checksum, and versioned flag. `RawFileInfo` can carry the entire `xl.meta` byte content.

Rename/delete/request parameter structs carry disk IDs, volumes, paths, options, and `FileInfo` snapshots across storage handlers. `RenameDataResp` returns a signature and old data directory to support two-phase cleanup of previous object data after metadata rename.

## Dependencies and integration points

The file depends on MinIO internal crypto detection, grid byte-buffer pooling, internal ioutil sizing constants, erasure metadata types, object part metadata, replication state, lifecycle/tiering helpers referenced by `FileInfo` methods defined elsewhere, and global constants such as `ReservedMetadataPrefix`, `ReservedMetadataPrefixLower`, `nullVersionID`, `erasureAlgorithm`, and `blockSizeV2`.

Integration points include storage REST/grid handlers, erasure set object operations, healing and quorum logic, metadata read/write/update/delete paths, multi-object delete, part verification, bulk delete, inline data rename paths, and msgp code generation. Because these structs are shared wire contracts, they are consumed by generated marshal/unmarshal code and by remote peers that may be running compatible but not identical versions.

## Risks and edge cases

- Field additions, deletions, or reordering in tuple-encoded structs can break internode compatibility and persisted metadata parsing.
- `FileInfo.Equals` intentionally compares selected semantic fields, not every field; callers must not use it as a full object metadata equality check.
- `InlineData` depends on metadata keys and remote-tier state; stale inline metadata from older versions is explicitly masked by `!fi.IsRemote()`.
- Buffer pooling in `RenameDataInlineHandlerParams.Recycle` requires callers to recycle once and avoid using `FI.Data` afterward.
- `findVersionIndex` treats empty requested version as invalid but `nullVersionID` as a special lookup for empty stored version IDs.
- Quorum helpers assume erasure fields are valid; malformed `FileInfo` could yield incorrect quorum or shard-size results.
- Request structs expose low-level file paths and disk IDs; validation must happen in handler code outside this file.

## Test signals

No tests for this file are included in this subset. Useful tests would cover `FileInfoVersions.Size`, null-version lookup, shard-size math for full/partial/zero/unknown lengths, quorum behavior for delete markers and equal data/parity layouts, inline data masking for remote objects, `GetDataDir` legacy/delete-marker cases, and buffer recycling behavior.
