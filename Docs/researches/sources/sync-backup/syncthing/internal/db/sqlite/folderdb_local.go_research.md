# sources/sync-backup/syncthing/internal/db/sqlite/folderdb_local.go

## Purpose
This file implements folder-local file retrieval, local iterators, block lookup, device listing, and human-readable debug output.

## Important APIs and Control Flow
`GetDeviceFile` normalizes a filename, joins `fileinfos`, `files`, `blocklists`, `devices`, and `file_names`, and reconstructs a `protocol.FileInfo`. `AllLocalFiles`, `AllLocalFilesBySequence`, and `AllLocalFilesWithPrefix` stream fileinfos for one device, optionally sequence-ordered or prefix-bounded. `AllLocalFilesWithBlocksHash` returns metadata for local files with a matching blocklist hash. `AllLocalBlocksWithHash` joins through live local `files` rows to filter out garbage-collected/deferred block rows. `ListDevicesForFolder` reports remote devices with positive counts. `DebugCounts` and `DebugFilePattern` print tabular diagnostic data with shortened device IDs, type names, versions, and blocklist hashes.

## State and Persistence Behavior
The code is mostly read-only, relying on stored protobuf fileinfos and blocklists. Debug methods expose internal persisted state but do not mutate it.

## Dependencies and Integration Points
It uses `db.FileMetadata`, `db.BlockMapEntry`, `indirectFI`, `dbVector`, filename normalization/native conversion, `tabwriter`, and `protocol.DeviceIDFromString`.

## Risks and Test Signals
Iterator error handling and row closing are important for long scans. Block lookup must avoid stale rows after file replacement. `db_local_test.go` and `db_test.go` provide coverage for file, prefix, sequence, block, and device-list behavior.
