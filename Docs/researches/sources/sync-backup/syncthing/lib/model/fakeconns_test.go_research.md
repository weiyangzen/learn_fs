# sources/sync-backup/syncthing/lib/model/fakeconns_test.go

## Purpose
Provides mocked protocol connections for model tests, including file advertisement, request data, deletion, update, and download progress capture.

## Important APIs, Types, and Functions
`downloadProgressMessage` records folder updates. `newFakeConnection` creates a `protocolmocks.Connection` wrapper. `fakeConnection` stores files, file data, folder ID, model reference, and close state. Helpers include `setIndexFn`, `DownloadProgress`, `addFileLocked`, `addFile`, `updateFile`, `deleteFile`, `sendIndexUpdate`, and `addFakeConn`.

## Control Flow
The fake connection returns bytes from `fileData` for protocol requests, reports stable IDs, and on close calls `model.Closed` once. File helpers build `protocol.FileInfo` with scanner blocks, monotonically increasing sequences, versions based on the fake device short ID, and type-specific metadata. `addFakeConn` attaches the fake to a `testModel` and sends cluster config.

## State and Persistence Behavior
All fake state is in memory, protected by a mutex for file mutations. It does not persist files to disk; file content lives in `fileData`. Sequence timestamps use `timeutil.StrictlyMonotonicNanos`.

## Dependencies and Integration Points
Depends on protocol mocks, scanner block generation, rand IDs, and the model test harness. It integrates with `Model.IndexUpdate`, `AddConnection`, and `ClusterConfig`.

## Risks
Mocks omit many real connection behaviors, such as streaming errors, latency, authentication, and partial request failures, unless tests override mock functions. `DownloadProgress` appends without locking.

## Test Signals
This is test infrastructure; its effectiveness is visible in folder, puller, and receive-only tests that need controllable remote devices.
