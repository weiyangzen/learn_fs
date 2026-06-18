# sources/sync-backup/syncthing/internal/db/sqlite/db_indexid_test.go

## Purpose
This test file validates per-folder, per-device index ID behavior. Index IDs identify a device's index stream and are persisted in the folder database `indexids` table.

## Important APIs and Control Flow
`TestIndexIDs` opens a temporary DB, then runs parallel subtests for local and remote devices. For `protocol.LocalDeviceID`, `GetIndexID` must lazily generate a nonzero ID, persist it, and return the same value on later calls. A separate folder must receive a different local ID. For a remote device, `GetIndexID` must return zero until `SetIndexID` stores an explicit value, after which it must be retrieved exactly.

## State and Persistence Behavior
The tests cover the distinction in `folderDB.GetIndexID`: local devices create state under `updateLock`, while non-local devices are read-only unless set explicitly. The folder wrapper creates folder DBs on `GetIndexID`, so even an ID lookup can create per-folder persistent state.

## Dependencies and Integration Points
The file depends on `protocol.NewIndexID`, `protocol.IndexID`, and the public `DB` methods that delegate to `folderdb_indexid.go` through `db_folderdb.go`.

## Risks and Test Signals
The test guards against accidental remote ID generation, local ID instability, and cross-folder reuse. It does not assert sequence preservation, which is covered in broader database tests.
