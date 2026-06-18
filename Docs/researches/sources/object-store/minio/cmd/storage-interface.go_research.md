# sources/object-store/minio/cmd/storage-interface.go

## Purpose

`storage-interface.go` defines `StorageAPI`, the central abstraction for a MinIO storage disk or remote disk endpoint. It is the contract implemented by local XL storage and remote storage clients and consumed by erasure/object-layer code, healing, scanners, and storage REST/grid handlers.

The interface groups disk identity/lifecycle, disk health, namespace scanning, volume operations, metadata operations, file operations, bulk reads, verification, cleanup, and disk location access behind a single contract.

## Important APIs, Types, And Functions

Identity and lifecycle methods include `String`, `IsOnline`, `LastConn`, `IsLocal`, `Hostname`, `Endpoint`, `Close`, `GetDiskID`, `SetDiskID`, `Healing`, `DiskInfo`, `NSScanner`, and `GetDiskLoc`.

Volume methods include `MakeVol`, `MakeVolBulk`, `ListVols`, `StatVol`, and `DeleteVol`.

Metadata/object-version methods include `DeleteVersion`, `DeleteVersions`, `DeleteBulk`, `WriteMetadata`, `UpdateMetadata`, `ReadVersion`, `ReadXL`, and `RenameData`.

File and data-plane methods include `WalkDir`, `ListDir`, `ReadFile`, `AppendFile`, `CreateFile`, `ReadFileStream`, `RenameFile`, `RenamePart`, `CheckParts`, `Delete`, `VerifyFile`, `StatInfoFile`, `ReadParts`, `ReadMultiple`, `CleanAbandonedData`, `WriteAll`, and `ReadAll`.

The interface references important storage datatypes from nearby files: `DiskInfoOptions`, `DiskInfo`, `VolInfo`, `WalkDirOptions`, `FileInfo`, `FileInfoVersions`, `DeleteOptions`, `UpdateMetadataOpts`, `ReadOptions`, `RawFileInfo`, `RenameOptions`, `RenameDataResp`, `BitrotVerifier`, `CheckPartsResp`, `StatInfo`, `ReadMultipleReq`, and `ReadMultipleResp`.

## Control Flow

This file declares no implementation, but it shapes caller control flow. Object-layer code can treat local and remote disks uniformly: inspect online state and disk identity, perform volume setup, read or mutate metadata, stream or bulk-read files, check parts, and clean abandoned data. `context.Context` appears on every potentially blocking operation, making cancellation and request scoping part of the contract.

`ReadMultiple` is asynchronous from the caller's perspective: it accepts a request and sends `ReadMultipleResp` values on a caller-provided channel. `WalkDir` streams a metacache representation to an `io.Writer`. `ReadFileStream` returns an `io.ReadCloser`, pushing resource management to the caller.

## State And Persistence Behavior

Implementations of this interface own persistent storage behavior: creating/deleting volumes, writing metadata, updating `xl.meta`, appending and creating files, renaming data directories, deleting object versions, and cleaning abandoned data. The interface distinguishes metadata writes from data writes and has explicit options for delete, rename, read, and metadata persistence.

`RenameData` returns `RenameDataResp`, which includes old data directory information for two-phase cleanup. `UpdateMetadataOpts.NoPersistence` can alter sync behavior for metadata updates. `DiskInfo` and `NSScanner` expose disk state and data-usage scanning to higher layers.

## Dependencies And Integration Points

The file imports `context`, `io`, `time`, and `github.com/minio/madmin-go/v3`. It integrates with MinIO's endpoint model, healing tracker, data-usage cache, metacache walking, bitrot verification, object part metadata, and storage REST/grid serialization. The generated msgp datatypes in `storage-datatypes_gen.go` support the wire representation for many of these interface methods when the implementation is remote.

## Risks

Because `StorageAPI` is broad, adding or changing a method affects every local and remote implementation, mocks, tests, and wrapper types. Method semantics must stay aligned across local disks and remote clients; otherwise erasure sets can behave differently depending on disk locality. The `CreateFile` signature contains an `olume` parameter name typo, harmless for callers but a readability hazard.

Concurrency, cancellation, stream closure, and partial-write semantics are implementation-sensitive and not enforced by the interface. Any method returning storage sentinel errors from `storage-errors.go` must preserve enough identity for higher layers to make availability and API decisions.

## Test Signals

The requested files do not include direct interface conformance tests. Signals should come from compile-time implementation checks elsewhere, storage REST/grid tests, erasure integration tests, healing/scanner tests, and tests that exercise local and remote disks through the same `StorageAPI` contract.
