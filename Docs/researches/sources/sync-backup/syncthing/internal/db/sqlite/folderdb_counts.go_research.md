# sources/sync-backup/syncthing/internal/db/sqlite/folderdb_counts.go

## Purpose
This file computes aggregate file counts and byte totals from the per-folder SQLite database.

## Important APIs and Control Flow
`countsRow` mirrors rows from the materialized `counts` table. `CountLocal` selects counts for a specific device excluding ignored rows. `CountNeed` dispatches to local or remote need-count SQL. `CountGlobal` selects rows marked `FlagLocalGlobal` and not invalid. `CountReceiveOnlyChanged` selects receive-only rows. `needSizeLocal` sums rows with `FlagLocalNeeded`. `needSizeRemote` mirrors remote need-list semantics using two grouped queries: valid non-deleted globals absent at the remote's same version, and valid deleted globals where the remote still has a valid non-deleted row. `summarizeCounts` converts rows into `db.Counts`.

## State and Persistence Behavior
The code is read-only and depends on count triggers in the folder schema staying synchronized with `files`. Deleted rows increment `Counts.Deleted`; files, directories, and symlinks increment separate counters and bytes.

## Dependencies and Integration Points
It depends on `db.Counts`, `protocol.FileInfoType`, `protocol.FlagLocal`, template constants from `baseDB.tplInput`, and SQL written by `folderdb_update.go`.

## Risks and Test Signals
The risk is divergence between count SQL and iterator SQL, especially remote deleted needs. `db_global_test.go` and `db_test.go` compare counts with need/global iterators across ignored, invalid, deleted, symlink, and directory cases.
