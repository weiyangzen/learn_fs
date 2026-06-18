# sources/sync-backup/syncthing/internal/db/sqlite/folderdb_global.go

## Purpose
This file implements global-file and need-list queries inside a single folder database.

## Important APIs and Control Flow
`GetGlobalFile` normalizes the name, selects the row marked `FlagLocalGlobal`, joins fileinfo and optional blocklist bytes, and reconstructs a `protocol.FileInfo`. `GetGlobalAvailability` finds remote devices holding the same version as the current global row. `AllGlobalFiles` and `AllGlobalFilesPrefix` stream global metadata ordered by name, using `prefixEnd` for prefix ranges. `AllNeededGlobalFiles` converts `config.PullOrder` to SQL ordering and appends limit/offset, then delegates to local or remote need queries. Local need selects rows with `FlagLocalNeeded` and not ignored. Remote need selects valid non-deleted global rows not present on the remote at the same version plus valid deleted globals when the remote has any valid non-deleted row for that name.

## State and Persistence Behavior
The file is read-only but depends on `folderdb_update.go` maintaining global and need flags. FileInfo rows are reconstructed from protobuf payloads plus optional external blocklists.

## Dependencies and Integration Points
It integrates with `config.PullOrder`, `protocol.DeviceID`, `db.FileMetadata`, `itererr.Map`, `indirectFI`, and filename normalization/native conversion.

## Risks and Test Signals
Dynamic `ORDER BY`, `LIMIT`, and `OFFSET` strings are built from controlled enum/int inputs, not user SQL. The main risk is remote need semantics around deleted or invalid rows. `db_global_test.go` is the primary coverage.
