# sources/sync-backup/syncthing/internal/db/sqlite/folderdb_update.go

## Purpose
This file contains the core write path for per-folder file index state, including file insertion/replacement, blocklist persistence, block index maintenance, global/need recalculation, drop operations, and WAL checkpoint pacing.

## Important APIs and Control Flow
`Update` locks the folder, ensures a device index, starts a transaction with cached prepared statements, normalizes names, computes block hashes, applies synthetic directory size, records remote sequence values, deduplicates file names and version strings, inserts/replaces file rows, stores external blocklists, optionally inserts local block rows, marshals `FileInfo` protobufs, and calls `recalcGlobalForFile` for each changed name. It rejects duplicate remote sequence numbers in one update batch. Drop methods remove devices or file rows and recalculate affected global state. `DropBlockIndex` deletes all block rows and vacuums; `PopulateBlockIndex` rebuilds from local file blocklists. `insertBlocksLocked` chunks inserts in batches of 1000 to avoid SQLite variable limits.

## State and Persistence Behavior
Persistent state spans `devices`, `file_names`, `file_versions`, `files`, `fileinfos`, `blocklists`, `blocks`, `indexids`, counts triggers, and WAL checkpoints. `recalcGlobalForFile` sorts all rows for a name by vector, invalid state, modified time, and device index, marks exactly one global row, and sets local need unless local already has the global/equivalent version or the global is invalid.

## Dependencies and Integration Points
The file depends on `protocol.FileInfo`, `db.UpdateOptions`, `dbproto.BlockList`, protobuf marshaling, `txPreparedStmts`, `dbVector`, `iterStructs`, and SQL template constants.

## Risks and Test Signals
This is the highest-risk file in the subset. Regressions can corrupt global state, need state, block lookup, sequences, or conflict resolution. Tests in `db_test.go`, `db_global_test.go`, and `db_local_test.go` cover concurrency, block-index rebuild, deleted conflict wins, large files, skipped block indexing, and drops.
