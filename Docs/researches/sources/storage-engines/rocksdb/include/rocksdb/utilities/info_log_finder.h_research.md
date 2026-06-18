# sources/storage-engines/rocksdb/include/rocksdb/utilities/info_log_finder.h

## Purpose
Declares a small utility for discovering information log files associated with an open RocksDB instance.

## Important APIs, Types, And Functions
`GetInfoLogList(DB* db, std::vector<std::string>* info_log_list)` returns a `Status` and populates the output list.

## Control Flow, State, And Persistence
The implementation is expected to inspect DB options/environment and log naming conventions, then list current and rotated info logs. It is read-only with respect to DB state and observes filesystem state.

## Dependencies And Integration Points
Depends on `DB`, `Options`, and `Status`. It supports operational diagnostics and log collection tooling.

## Risks And Edge Cases
Custom log directories, concurrent log rotation, missing files, environment errors, and null pointers are the main edge cases. Ordering should not be assumed unless the implementation guarantees it.

## Test Signals
Cover default and custom log paths, rotated logs, empty directories, deleted-during-list files, and filesystem errors.
