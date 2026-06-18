# sources/storage-engines/rocksdb/examples/column_families_example.cc

## Purpose
`column_families_example.cc` demonstrates creating, reopening, using, writing atomically across, dropping, and destroying handles for RocksDB column families.

## Important APIs and control flow
The example opens a DB with `Options::create_if_missing`, creates column family `"new_cf"`, destroys its handle, and closes the DB. It then reopens with a `std::vector<ColumnFamilyDescriptor>` containing both `kDefaultColumnFamilyName` and `"new_cf"`, receiving parallel `ColumnFamilyHandle*` entries. It writes and reads a key in the non-default family, then uses `WriteBatch` to put into both families and delete from the default family. Finally it drops the non-default family and destroys every handle before closing.

## State, persistence, and integration
The DB path is a platform-specific temp directory. Persistent state includes the created column family metadata and key/value data. The example integrates with `rocksdb/db.h`, `rocksdb/options.h`, `rocksdb/slice.h`, `DBOptions`, `ColumnFamilyOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, and `WriteBatch`.

## Risks and test signals
The fixed temp path can collide with previous runs, and the example does not call `DestroyDB`, so stale DB state can affect repeated execution. It uses raw handles and manual destruction, which is correct for the API but easy to leak in real code. It asserts only status success, not all resulting values. Test signals are successful open with explicit default CF, correct handle count/order, successful `Put`/`Get` on `handles[1]`, successful cross-CF `WriteBatch`, `DropColumnFamily`, and handle destruction without leaks or status failures.
