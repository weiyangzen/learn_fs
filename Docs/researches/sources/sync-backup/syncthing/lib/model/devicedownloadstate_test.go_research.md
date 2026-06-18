# sources/sync-backup/syncthing/lib/model/devicedownloadstate_test.go

## Purpose
Validates device download progress state transitions across versions, appends, forgets, and multiple files.

## Important APIs, Types, and Functions
`TestDeviceDownloadState` builds `protocol.FileDownloadProgressUpdate` fixtures for two versions of `f1` and one version of `f2`, then drives `newDeviceDownloadState`, `Update`, and `Has`.

## Control Flow
Each table row applies a sequence of updates to a fresh state, then iterates expected present and absent block indexes. Scenarios cover append accumulation, matching-version forget, nonmatching forget no-op, version replacement, delete then append, and multi-file isolation.

## State and Persistence Behavior
Only in-memory state is created per table row. No persisted database or filesystem state.

## Dependencies and Integration Points
Uses `protocol.Vector` and `protocol.FileDownloadProgressUpdate`, matching messages sent over Syncthing connections.

## Risks
Does not test `BytesDownloaded`, `GetBlockCounts`, nil receiver behavior, folder isolation beyond one folder name, or concurrent access.

## Test Signals
Strong signal that block availability is version-scoped and stale progress is cleared when remote devices switch file versions.
