# sources/storage-engines/rocksdb/tools/reduce_levels_test.cc

## Purpose
This GoogleTest suite validates the `ldb reduce_levels` command. It ensures that RocksDB databases can be reopened with fewer LSM levels after moving existing files down into the reduced level structure, without losing keys.

## Important APIs, Types, and Functions
`ReduceLevelTest` wraps a temporary DB path and a `std::unique_ptr<DB>`. It exposes `OpenDB`, `Put`, `Get`, `Flush`, `MoveL0FileToLevel`, `CloseDB`, `ReduceLevels`, and `FilesOnLevel`. Internally it uses `DBImpl::TEST_FlushMemTable`, `DBImpl::TEST_CompactRange`, `ReduceDBLevelsCommand::PrepareArgs`, and `LDBCommand::InitFromCmdLineArgs`.

## Control Flow
Tests create DBs with a fixed number of levels, write and flush keys, force compaction from L0 to target levels, close the DB, invoke the reduce-level command offline, reopen with the new level count, and assert file placement or key readability. `Last_Level` repeatedly collapses a DB with data at the bottom level. `Top_Level` validates reductions with only L0 data. `All_Levels` populates levels 1 through 4, then reduces to 4, 3, and 2 levels while verifying all keys.

## State and Persistence
The test manipulates real RocksDB files under a per-thread path. The reduce command persists updated metadata such that reopening with fewer `num_levels` succeeds. Data persistence is validated through `Get` after each reduction.

## Dependencies and Integration Points
It integrates DB internals, `tools/ldb_cmd_impl.h`, `util/cast_util.h`, and RocksDB test harness utilities. It directly selects the ldb command implementation rather than spawning a process.

## Risks
The test uses internal `TEST_` DBImpl methods and static casting, making it sensitive to compaction internals. It only tests default column family and basic value keys. It does not assert detailed manifest edits beyond reopen and file-count behavior.

## Test Signals
Passing tests signal that level-reduction command arguments, offline manifest edits, and DB recovery with reduced level counts work for top-level, bottom-level, and multi-level file layouts.
