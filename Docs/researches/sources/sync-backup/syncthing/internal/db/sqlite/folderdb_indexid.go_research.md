# sources/sync-backup/syncthing/internal/db/sqlite/folderdb_indexid.go

## Purpose
This file manages per-device index IDs and per-device sequence tracking in a folder database.

## Important APIs and Control Flow
`GetIndexID` first tries a read-only join over `indexids` and `devices`. If absent for a remote device, it returns zero. If absent for the local device, it takes `updateLock`, rechecks, generates `protocol.NewIndexID`, and inserts it with the current max local file sequence. `SetIndexID` ensures a device row and stores a supplied ID with sequence zero. `DropAllIndexIDs` clears all IDs. `GetDeviceSequence` returns the stored sequence or zero for missing/null values. `RemoteSequences` streams non-local device sequence rows and parses device IDs. `indexIDFromHex` and `indexIDToHex` convert protocol IDs to/from database strings.

## State and Persistence Behavior
State lives in the `indexids` table keyed by `device_idx`; `files` inserts update sequence through schema behavior. The local lazy insert preserves current local max sequence to avoid resetting an existing file stream.

## Dependencies and Integration Points
The file depends on `protocol.IndexID`, `protocol.DeviceID`, `iterStructs`, `itererr.Zip`, and `deviceIdxLocked`.

## Risks and Test Signals
Hex conversion and local lazy creation are critical. Remote IDs must not be created accidentally. `db_indexid_test.go`, `db_local_test.go`, and `db_test.go` cover ID persistence and sequences.
