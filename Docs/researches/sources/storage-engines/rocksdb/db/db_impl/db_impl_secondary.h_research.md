# sources/storage-engines/rocksdb/db/db_impl/db_impl_secondary.h

## sources/storage-engines/rocksdb/db/db_impl/db_impl_secondary.h

### Purpose

`db_impl_secondary.h` declares the secondary-mode `DBImpl` subclass and a small WAL-reader owner used by the implementation. It defines the contract for a read-only secondary instance that can replay primary MANIFEST/WAL state without coordinating through the primary's process and rejects all user mutations. It also declares the private helpers used by remote compaction through `DB::OpenAndCompact()`.

### Important APIs, Types, And Functions

- `LogReaderContainer` owns a `log::FragmentBufferedReader`, its reporter, and a `Status` recording WAL corruption. Its nested reporter logs dropped bytes and stores the first corruption status.
- `DBImplSecondary` derives from `DBImpl` and overrides recovery, reads, iterators, write/mutation APIs, file deletion toggles, flush/options changes, WAL sync, external-file ingestion, and catch-up.
- `Recover()` is declared to replay MANIFEST only and initialize `manifest_reader_` for later catch-up.
- `GetImpl()`, `NewIterator()`, `NewIteratorImpl()`, and `NewIterators()` provide the read surface.
- Mutation APIs such as `Put`, `PutEntity`, `Merge`, `Delete`, `SingleDelete`, `Write`, `CompactRange`, `CompactFiles`, `Flush`, `SetDBOptions`, `SetOptions`, `SyncWAL`, and file ingestion APIs return `Status::NotSupported("Not supported operation in secondary mode.")`.
- `TryCatchUpWithPrimary()` is the public secondary refresh hook.
- `TEST_CompactWithoutInstallation()` exposes remote compaction internals in debug builds.
- `CompactionProgressFilesScan` captures one scan of the secondary workspace: latest progress file, old progress files, temp progress files, and table-file numbers.

### Control Flow

The header makes secondary behavior explicit before the implementation starts. Normal `DBImpl` overloads are brought into scope with `using`, then write-like overloads are overridden inline to fail fast. This prevents accidental mutation through a secondary pointer even though `DBImplSecondary` still inherits the full `DBImpl` machinery. Reads and catch-up are declared for implementation in the `.cc` file, while `FlushForGetLiveFiles()` is overridden as a read-only no-op and `OwnTablesAndLogs()` is overridden to return false.

Remote compaction helpers are private and friend-only through `DB`, so the public API remains `DB::OpenAndCompact()` rather than direct `DBImplSecondary` construction. `OpenAsSecondaryImpl()` accepts `recover_wal` so one implementation can serve both normal secondaries and remote compaction.

### State And Persistence Behavior

`manifest_reader_`, `manifest_reporter_`, and `manifest_reader_status_` keep MANIFEST tailing state between catch-up attempts. `log_readers_` caches WAL readers by log number so repeated catch-up can continue reading existing WALs instead of reopening from the beginning. `cfd_to_current_log_` tracks which WAL populated each column family's active memtable. `secondary_path_` is the persistent workspace path for secondary metadata/logs and remote compaction outputs. `compaction_progress_` is in-memory progress loaded from or persisted to compaction-progress files.

`LogReaderContainer` deliberately enables WAL checksumming even when paranoid checks would otherwise be false, because replaying corrupt sequence metadata into a secondary could make future reads unsafe. The reporter stores errors in its owned `Status` until the implementation consumes or permits them.

### Dependencies And Integration Points

The header depends on `db/db_impl/db_impl.h`, RocksDB logging, log reader types, `Status`, `ColumnFamilyData`, `CompactionServiceInput/Result`, and option/read/write API types inherited from `DBImpl` and `DB`. Its public behavior matches comments in `include/rocksdb/db.h` for `OpenAsSecondary()` and `TryCatchUpWithPrimary()`.

### Risks And Edge Cases

- Because `DBImplSecondary` inherits a large mutable base class, missing an override for a newly added mutation API could accidentally expose writes in secondary mode. Future DB API additions should be audited against this class.
- `OwnTablesAndLogs() == false` is a core safety assumption: cleanup must not delete primary-owned files. Any future secondary-owned linking/copying feature must revisit this.
- `LogReaderContainer` uses raw pointers internally and deletes them in its destructor. Ownership is simple but non-RAII within the class body, so constructor changes must preserve exception/error safety assumptions used by C++ builds without exceptions.
- The comments mention a workaround through `max_open_files=-1`, but typo-level drift in comments ("talbe") signals this area is operationally subtle and should be kept clear in user-facing docs.
- Progress scanning stores filenames and file numbers from one directory snapshot. Callers must avoid assuming it remains current after concurrent filesystem changes.

### Test Signals

Compile coverage is important for this header because it overrides many virtual APIs. Behavioral tests should attempt every mutation class against an opened secondary and assert `NotSupported`, exercise `GetLiveFiles()` without flushing, verify `TryCatchUpWithPrimary()` remains exposed through `DB`/`StackableDB`/C API surfaces, and run remote-compaction debug tests that use `TEST_CompactWithoutInstallation()`. Static research only; no build or test command was run for this report.
