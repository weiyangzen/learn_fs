# sources/sync-backup/syncthing/lib/model/devicedownloadstate.go

## Purpose
Tracks which blocks a remote device has downloaded into temporary files, enabling other devices to request already-downloaded temporary blocks and display remote progress.

## Important APIs, Types, and Functions
`deviceFolderFileDownloadState` stores block indexes, version, and block size per file. `deviceFolderDownloadState` manages files for one folder with `Has`, `Update`, `BytesDownloaded`, and `GetBlockCounts`. `deviceDownloadState` wraps all folders for a device with folder-scoped `Update`, `Has`, `GetBlockCounts`, `BytesDownloaded`, and `newDeviceDownloadState`.

## Control Flow
Updates are append or forget events. Append creates file state, replaces it if the version changes, or appends block indexes for the same version. Forget deletes only when the version matches. Queries first check nil receiver and folder/file existence, then require exact version equality.

## State and Persistence Behavior
All state is in-memory and guarded by RW mutexes. It is not persisted; it mirrors live `DownloadProgress` protocol messages. `BytesDownloaded` estimates using the advertised block size, falling back to `protocol.MinBlockSize`.

## Dependencies and Integration Points
Depends on `protocol.FileDownloadProgressUpdate` and `protocol.Vector`. Integrated with connection download progress handling and block availability from temporary files.

## Risks
Repeated append updates can duplicate block indexes, inflating counts and bytes if senders repeat data. Folder creation in `Update` uses a read-then-write pattern that could race if two goroutines create the same folder simultaneously, although subsequent map assignment is locked. Returned maps are snapshots.

## Test Signals
`devicedownloadstate_test.go` verifies append, replacement by version, forget semantics, and multi-file behavior. Byte-count and concurrent behavior are not directly tested there.
