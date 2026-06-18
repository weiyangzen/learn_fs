# sources/sync-backup/syncthing/internal/db/sqlite/db_global_test.go

## Purpose
This test file exercises global-version selection and "need" calculations in the SQLite backend. It verifies how local and remote file rows interact when versions differ, files are deleted, ignored, invalid, or absent, and when devices or file rows are dropped.

## Important APIs and Control Flow
Tests drive the public `DB` API: `Open`, `Update`, `AllNeededGlobalFiles`, `CountNeed`, `CountGlobal`, `GetGlobalFile`, `DropAllFiles`, `DropDevice`, and `DropFilesNamed`. `TestNeed` sets local and remote vectors to prove local need and remote need are symmetric but not identical. `testDropWithDropper` abstracts three drop paths and asserts global recalculation after removing a winning remote row. The later tests focus on deleted globals, ignored local rows, remote invalid flags, missing deleted rows, pagination, symlink/directory need accounting, and a regression where a delete after a conflict must become global.

## State and Persistence Behavior
Each test creates a temporary SQLite database and writes file state into per-folder databases. The assertions depend on `folderdb_update.go` setting `FlagLocalGlobal` and `FlagLocalNeeded`, and on `folderdb_global.go` querying those flags correctly. Deleted files contribute to deleted counts rather than bytes; directories use synthetic size semantics from update code.

## Dependencies and Integration Points
The file uses `config.PullOrder*`, `protocol.FileInfo`, `protocol.Vector`, and helper constructors in `db_test.go`. It is the main behavioral test signal for `recalcGlobalForFile`, remote need SQL, count summarization, and public folder-device drop methods.

## Risks and Test Signals
The risk surface is subtle conflict resolution: invalid or ignored rows must not become needed or counted as valid globals, while delete rows must still win when their version vector does. Pagination tests ensure `LIMIT/OFFSET` are appended safely to need queries. The "deleted after conflict" regression captures a real-world global-selection bug and should be preserved around vector serialization or comparison changes.
