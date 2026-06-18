# sources/storage-engines/rocksdb/include/rocksdb/utilities/option_change_migration.h

## Purpose
Declares best-effort utilities that restructure an existing DB so it can be reopened with changed options.

## Important APIs, Types, And Functions
Single-CF `OptionChangeMigration(dbname, old_opts, new_opts)` and multi-CF `OptionChangeMigration(dbname, old_db_opts, old_cf_descs, new_db_opts, new_cf_descs)`.

## Control Flow, State, And Persistence
The migration prepares data layout compatibility, potentially through full compaction or LSM restructuring, then expects callers to reopen with new options. It mutates persistent DB/table state but does not itself apply new options to future opens.

## Dependencies And Integration Points
Depends on `DB`, `Options`, `ColumnFamilyDescriptor`, and `Status`. Integrates with operational option migrations and compaction-style changes.

## Risks And Edge Cases
Best-effort only. Single-CF version is limited to one column family. Multi-CF version requires identical CF count, names, and order and does not add/drop CFs. Migrating to FIFO with a low max table-file size can drop the DB after migration if data exceeds the limit.

## Test Signals
Cover successful migration/reopen, CF validation errors, failure propagation, full compaction behavior, and FIFO threshold warning scenarios.
