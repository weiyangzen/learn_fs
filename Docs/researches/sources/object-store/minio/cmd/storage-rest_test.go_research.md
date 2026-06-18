# sources/object-store/minio/cmd/storage-rest_test.go

Purpose: integration-style tests for the storage REST client/server pair using a two-host in-process `grid` setup and real temporary `xlStorage`.

Important APIs/types/functions: helper tests cover `DiskInfo`, `StatInfoFile`, `ListDir`, `ReadAll`, `ReadFile`, `AppendFile`, `Delete`, and `RenameFile`. `newStorageRESTHTTPServerClient` builds the test grid, endpoint, pool metadata, registers storage REST handlers on both nodes, creates volumes, waits for remote disk info to become reachable, and returns a `storageRESTClient`.

Control flow: each `TestStorageRESTClient*` obtains a fresh remote client and runs a helper against the `StorageAPI` interface. Helpers create files through the remote client, then verify reads, stats, directory listings, deletion idempotence, rename behavior, and error classification for missing files or volumes. Append tests include path names with whitespace/control-like characters and skip those cases on Windows.

State and persistence behavior: tests create real volumes and files in temporary directories behind `xlStorage`. Global MinIO host/port and node auth token are adjusted during client creation; cleanup hooks tear down the grid and temp roots.

Dependencies/integration: depends on `grid.SetupTestGrid`, endpoint parsing/locality update, `registerStorageRESTHandlers`, `newStorageRESTClient`, `globalLocalSetDrives`, and low-level storage APIs. This file validates the protocol boundary between `storage-rest-client.go`, `storage-rest-server.go`, and `xlStorage`.

Risks/test signals: good signal for representative REST/grid connectivity and path encoding, but it does not cover every `StorageAPI` method in the remote client. Disk info expectation is tied to an unformatted disk state, and global host/port mutation requires careful cleanup to avoid order sensitivity.
