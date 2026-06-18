# sources/object-store/minio/cmd/xl-storage_noatime_notsupported.go

## Purpose
This platform-specific file defines read and write open flags for platforms where MinIO does not use Linux `O_NOATIME`/`O_DSYNC` behavior, namely non-Unix plus Darwin and FreeBSD builds.

## Important APIs, Types, and Functions
It exports package variables `readMode = os.O_RDONLY` and `writeMode = os.O_SYNC`. These variables are consumed by `xl-storage.go` when opening files for metadata and data reads/writes.

## Control Flow
There is no runtime control flow; build tags select this file at compile time. Storage reads open normally, and sync metadata writes use `os.O_SYNC` when `openFileSync` combines `writeMode` with `os.O_WRONLY`.

## State and Persistence Behavior
The file affects persistence semantics indirectly. `O_SYNC` asks the kernel to make writes synchronous on platforms in this build set, while read opens update access times according to platform defaults.

## Dependencies and Integration Points
The only dependency is Go's `os` package. The variables integrate with `readMetadataWithDMTime`, `readAllDataWithDMTime`, `ReadFile`, `ReadFileStream`, `AppendFile`, `writeAllInternal`, and other `xlStorage` open paths.

## Risks and Test Signals
Risk is platform divergence: Darwin/FreeBSD/non-Unix may have different sync and atime cost from Linux. Test coverage is indirect through the cross-platform storage tests; there is no specific test for these flag values.
