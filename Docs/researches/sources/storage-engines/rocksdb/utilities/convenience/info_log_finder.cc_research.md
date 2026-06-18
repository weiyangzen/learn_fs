# sources/storage-engines/rocksdb/utilities/convenience/info_log_finder.cc

## Purpose
This file implements a convenience helper that lists RocksDB info log files for an open DB.

## Important APIs, Types, and Functions
`GetInfoLogList(DB* db, std::vector<std::string>* info_log_list)` validates the DB pointer, reads the DB's options and name, and delegates to `GetInfoLogFiles`.

## Control Flow
If `db` is null, the function returns `InvalidArgument`. Otherwise it obtains `options.env->GetFileSystem()`, `options.db_log_dir`, and `db->GetName()`, then calls the filename utility to populate the output list.

## State and Persistence Behavior
The function is read-only. It may query filesystem metadata but does not mutate DB or log files.

## Dependencies and Integration Points
It depends on the public `rocksdb/utilities/info_log_finder.h`, filename utilities, and DB/Env APIs. It is a thin public utility over lower-level log-file discovery.

## Risks and Edge Cases
Only the DB pointer is validated locally; a null output vector or invalid environment would fail in delegated code. The returned list depends on filename parsing and the DB's configured log directory. Errors from filesystem traversal are returned directly.

## Test Signals
Tests should cover null DB rejection, default and custom `db_log_dir`, rotated logs, and empty/missing log directories.
