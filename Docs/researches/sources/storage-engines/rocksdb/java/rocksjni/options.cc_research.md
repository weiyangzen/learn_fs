# Research: sources/storage-engines/rocksdb/java/rocksjni/options.cc

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008650`: lines 1-7872, `Docs/researches/chunks/subset-b-008650_research.md`
- `subset-b-008651`: lines 7873-8810, `Docs/researches/chunks/subset-b-008651_research.md`

## Chunk Research

### subset-b-008650: lines 1-7872

# sources/storage-engines/rocksdb/java/rocksjni/options.cc lines 1-7872

## Scope

This chunk covers the first 7,872 lines of RocksDB's Java JNI options bridge. It starts with the native implementation for `org.rocksdb.Options`, continues through the full `org.rocksdb.ColumnFamilyOptions` bridge, and then covers the beginning and most of the `org.rocksdb.DBOptions` bridge through `DBOptions.setMaxBgErrorResumeCount`. The remaining tail of `DBOptions` plus `WriteOptions`, `ReadOptions`, `ComparatorOptions`, and `FlushOptions` continue after this chunk and are out of scope here.

The file is intentionally broad and mostly mechanical: each JNI entry point translates Java handles, primitive values, strings, arrays, callbacks, and enum bytes into fields or helper method calls on RocksDB C++ `Options`, `ColumnFamilyOptions`, and `DBOptions` objects. The nontrivial behavior is in native object ownership, Java/C++ array conversion, status-to-exception handling, enum conversion through portal helpers, shared-pointer copying, callback lifetime expectations, and option-string parsing.

## Purpose

- Expose the combined `rocksdb::Options` object to Java, including construction from separate `DBOptions` and `ColumnFamilyOptions`, copying, disposal, and optimization helpers.
- Expose standalone `ColumnFamilyOptions` and `DBOptions` objects so Java callers can configure DB-wide and column-family-specific state independently.
- Let Java configure core RocksDB behavior that is ultimately consumed by DB open, recovery, WAL handling, memtables, table factories, compaction, blob files, logging, statistics, rate limiting, and event callbacks.
- Convert Java-friendly values into C++ option fields: `jboolean` to bool, `jbyte` enum ordinals to RocksDB enums, `jlong` handles to C++ pointers, Java strings to `std::string`, and Java arrays to C++ vectors.
- Preserve ownership boundaries between Java wrapper objects and native RocksDB objects by copying `std::shared_ptr` instances where expected, taking raw ownership for factories stored in `unique_ptr` fields, and storing raw callback pointers for comparator/filter/WAL callback APIs.
- Provide parsing entry points for option-property strings through `GetColumnFamilyOptionsFromString()` and `GetDBOptionsFromString()`.

## Important APIs, Types, And Functions

- `Java_org_rocksdb_Options_newOptions__`, `newOptions__JJ`, `copyOptions`, and `disposeInternalJni` allocate, combine, clone, and delete native `rocksdb::Options` instances returned to Java as `jlong` handles.
- `Java_org_rocksdb_ColumnFamilyOptions_newColumnFamilyOptions`, `copyColumnFamilyOptions`, `newColumnFamilyOptionsFromOptions`, and `disposeInternalJni` provide the same lifecycle for `rocksdb::ColumnFamilyOptions`.
- `Java_org_rocksdb_DBOptions_newDBOptions`, `copyDBOptions`, `newDBOptionsFromOptions`, and `disposeInternalJni` provide the lifecycle for `rocksdb::DBOptions`.
- `getColumnFamilyOptionsFromProps` and `getDBOptionsFromProps` allocate new option objects, parse semicolon/property-style option strings with optional `ConfigOptions`, return `0` on parse failure, and delete failed allocations to avoid leaks.
- Comparator bridge methods accept either built-in comparator IDs or Java/native comparator handles. Built-in ID `1` maps to `ReverseBytewiseComparator()`, and the default maps to `BytewiseComparator()`. Custom handles are stored as raw `Comparator*`.
- Merge, compaction filter, WAL filter, event listener, logger, table filter, and table-property collector hooks integrate Java callbacks or wrapper objects with native `Options` fields.
- Shared resource setters copy `std::shared_ptr` payloads from Java-owned wrapper handles into option fields, including `StatisticsJni`, `RateLimiter`, `SstFileManager`, `Cache` row cache, `WriteBufferManager`, `CompactionFilterFactory`, `SstPartitionerFactory`, and `ConcurrentTaskLimiter`.
- Factory setters such as `setMemTableFactory` and `setTableFactory` reset native `unique_ptr` fields from raw handles, transferring ownership to the options object.
- `rocksdb_convert_cf_paths_from_java_helper()` validates Java path and size arrays, rejects mismatched lengths and negative target sizes, and returns `std::vector<DbPath>` for both `Options` and `ColumnFamilyOptions`.
- `rocksdb_convert_cf_paths_to_java_helper<T>()` writes native `cf_paths` back into caller-provided Java string and long arrays for either `Options` or `ColumnFamilyOptions`.
- `Options.setDbPaths` and `DBOptions.setDbPaths` separately convert DB path arrays. Unlike the shared CF-path helper, these functions do not explicitly check matching path/size lengths before indexing the Java long array.
- `rocksdb_set_event_listeners_helper()` and `rocksdb_get_event_listeners_helper()` convert between Java arrays of listener native handles and C++ vectors of `std::shared_ptr<EventListener>`, assuming the listeners are Java-backed `EventListenerJniCallback` objects on readback.
- `rocksdb_compression_vector_helper()` and `rocksdb_compression_list_helper()` translate per-level compression arrays between Java `byte[]` and `std::vector<CompressionType>`.
- Portal conversions in `rocksjni/portal.h` handle enum mappings for `CompressionType`, `CompactionStyle`, `CompactionPriority`, `WALRecoveryMode`, and `PrepopulateBlobCache`.
- Option tuning wrappers call native helpers: `IncreaseParallelism`, `OldDefaults`, `OptimizeForSmallDb`, `OptimizeForPointLookup`, `OptimizeLevelStyleCompaction`, `OptimizeUniversalStyleCompaction`, and `PrepareForBulkLoad`.
- Getter/setter pairs cover DB-open flags, file IO behavior, background jobs, logging, WAL retention and recovery, write-thread behavior, stats persistence, direct IO, memtable sizing, compression, compaction triggers, universal/FIFO compaction options, blob file options, and range deletion conversion thresholds.

## Control Flow

The normal flow for a Java options object starts with a Java wrapper calling a native constructor. The C++ side allocates the corresponding RocksDB option object with `new`, casts its address through `GET_CPLUSPLUS_POINTER`, and returns it as a `jlong`. Later Java setter calls pass that handle back; the JNI function casts it to the expected C++ type and mutates one field or invokes one RocksDB option helper. Disposal casts the handle back and deletes it, guarded only by an `assert` against null.

For composite `Options`, `newOptions__JJ` takes already-created `DBOptions` and `ColumnFamilyOptions` handles, dereferences both, and constructs a combined `rocksdb::Options(*dbOpt, *cfOpt)`. Conversely, `newColumnFamilyOptionsFromOptions` and `newDBOptionsFromOptions` project the relevant base subobject out of a combined `Options`.

String setters usually call `GetStringUTFChars`, check for null or exception, assign to a `std::string`, and release the UTF chars. Parsing functions follow a similar flow but run `GetColumnFamilyOptionsFromString()` or `GetDBOptionsFromString()` before returning a handle. If parsing fails, the freshly allocated option object is deleted and Java receives `0` rather than a thrown exception in this chunk.

Array conversion follows a defensive JNI pattern in most helpers: obtain array elements, loop over entries, create or copy C++ values, check `ExceptionCheck()` after object-array writes, release with `JNI_ABORT` when Java input arrays should not be modified, and release with commit mode when writing native data into Java output arrays. Compression and multiplier arrays allocate temporary C++ buffers, fill Java primitive arrays, and delete the temporary buffers on both success and exception paths.

Callback and shared-resource setters are mostly direct handle transfers. Shared-pointer-backed wrappers are dereferenced and copied into the native option object so lifetime is extended by C++ ownership. Raw callback pointers such as comparators, compaction filters, WAL filters, and table filters are stored directly, so the Java wrapper layer must keep the callback object alive as long as the native options or opened DB can use it.

The `DBOptions` section mirrors many `Options` DB-wide setters. This chunk stops while processing background-error resume options, so later `DBOptions` properties are documented by the next chunk.

## State And Persistence Behavior

The JNI code itself does not write persistent data. It mutates in-memory option structures whose values are later consumed by RocksDB open, write, flush, compaction, recovery, and administrative code. Some fields configured here affect persistent behavior indirectly:

- `create_if_missing`, `create_missing_column_families`, `error_if_exists`, and `paranoid_checks` control DB open and recovery semantics.
- WAL fields such as `max_total_wal_size`, `WAL_ttl_seconds`, `WAL_size_limit_MB`, `wal_recovery_mode`, `allow_2pc`, `two_write_queues`, `manual_wal_flush`, `atomic_flush`, and `write_dbid_to_manifest` affect recovery, WAL retention, transaction support, and MANIFEST contents once a DB is opened.
- File and manifest options such as `db_paths`, `cf_paths`, `db_log_dir`, `wal_dir`, `max_manifest_file_size`, `manifest_preallocation_size`, `use_fsync`, mmap/direct IO flags, `bytes_per_sync`, `wal_bytes_per_sync`, and `strict_bytes_per_sync` influence where RocksDB stores files and how durable/synchronized writes are performed.
- Memtable and write-buffer options influence flush frequency and write stalls, including `write_buffer_size`, `max_write_buffer_number`, `min_write_buffer_number_to_merge`, `db_write_buffer_size`, `write_buffer_manager`, and `allow_concurrent_memtable_write`.
- Compaction options influence future SST layout and rewrite behavior: compression settings, level sizes, L0 triggers, compaction style, compaction priority, dynamic level bytes, universal/FIFO options, TTL, periodic compaction, and blob garbage collection knobs.
- `Statistics`, event listeners, loggers, table property collectors, rate limiters, caches, partitioners, and factories stored here become dependencies of the DB or column family created from these options.

Native ownership state is important. Objects allocated in this chunk are owned by Java wrapper handles until `disposeInternalJni` is called. Options fields may then own copied `shared_ptr` references or `unique_ptr` factories. Some returned getters allocate new native wrapper state, such as statistics shared-pointer copies and table-property collector wrapper arrays; Java must dispose those according to the corresponding Java wrapper contract.

## Dependencies And Integration Points

- JNI headers and generated Java headers define the exported names and method signatures for `Options`, `ColumnFamilyOptions`, `DBOptions`, `WriteOptions`, `ReadOptions`, `ComparatorOptions`, and `FlushOptions`.
- Core RocksDB option types come from `rocksdb/options.h`, `rocksdb/db.h`, `rocksdb/table.h`, `rocksdb/comparator.h`, `rocksdb/memtablerep.h`, `rocksdb/merge_operator.h`, `rocksdb/rate_limiter.h`, `rocksdb/slice_transform.h`, `rocksdb/sst_partitioner.h`, and `rocksdb/statistics.h`.
- Convenience parsing uses `rocksdb/convenience.h` and `ConfigOptions`.
- Built-in merge operator lookup uses `utilities/merge_operators.h`.
- Java callback integration depends on RocksJNI callback classes and portal helpers: comparator callbacks, logger callbacks, event listener callbacks, WAL/table filters, table-property collector factories, statistics wrappers, `CplusplusToJavaConvert`, and enum conversion helpers in `rocksjni/portal.h`.
- Public Java API integration is through `org.rocksdb.Options`, `ColumnFamilyOptions`, `DBOptions`, and related Java wrappers that hold the `nativeHandle_` values passed into these functions.
- Runtime integration happens when RocksJava passes these populated option objects to DB open, column-family creation, compaction configuration, iterator/read/write paths, and recovery.

## Risks And Edge Cases

- Most setters trust the incoming `jlong` handle type. Passing a stale handle or a handle for the wrong option class can corrupt memory because the code uses `reinterpret_cast` without runtime type checks.
- Many numeric setters cast signed Java values to unsigned or narrower native types. A subset uses `JniUtil::check_if_jlong_fits_size_t()`, but many fields do not reject negative Java values before casting to `uint64_t`, `size_t`, or `uint32_t`.
- `Options.setDbPaths` and `DBOptions.setDbPaths` index the target-size array in parallel with the path array without the length check used by `rocksdb_convert_cf_paths_from_java_helper()`.
- `dbPaths()` and `cfPaths()` assume the caller-provided Java output arrays are at least as long as the native vector length being read. Bounds failures are handled as Java exceptions after the attempted write, but native code has already indexed `opt->*_paths[i]` according to the Java array length.
- Some readback functions write `DbPath::target_size` into a `jlong` array through `static_cast<jint>`, which can truncate large target sizes.
- Raw callback fields (`Comparator*`, `CompactionFilter*`, `WalFilter*`, table filters) require Java-side lifetime discipline. The options object does not copy or own all of these callback objects.
- `setMemTableFactory` and `setTableFactory` transfer raw pointer ownership into `unique_ptr` fields. Reusing the same native factory handle elsewhere after transfer risks double deletion or use-after-free.
- Event listener readback assumes every stored listener is an `EventListenerJniCallback` and `static_cast`s from `EventListener*`; native C++ listeners added in the future would break that assumption.
- Logger setters validate unknown logger type bytes, but comparator-type setters do not throw on unknown bytes and can leave the comparator null.
- Several getters allocate new native wrappers or arrays of wrapper handles. Leaks are possible if Java code does not dispose returned wrapper handles.
- Parse-from-string APIs return `0` on invalid input rather than throwing here. Java callers must translate or check the zero handle correctly.
- The chunk contains many duplicated `Options`, `ColumnFamilyOptions`, and `DBOptions` setters. A field added to one class can easily be missed in the others, causing Java API drift from C++ options.

## Test Signals

- RocksJava option lifecycle tests should cover constructor/copy/dispose paths for `Options`, `ColumnFamilyOptions`, and `DBOptions`, including constructing combined `Options` from separate DB/CF options.
- Property-string tests should cover successful and failed `getColumnFamilyOptionsFromProps` and `getDBOptionsFromProps`, with and without explicit `ConfigOptions`, and confirm failed parses do not return live handles.
- JNI conversion tests should exercise DB paths, CF paths, compression-per-level arrays, max-bytes multiplier arrays, event listener arrays, and table-property collector factory arrays, including mismatched lengths and large target sizes.
- Enum mapping tests should cover compression type, bottommost compression, blob compression, compaction style, compaction priority, WAL recovery mode, and prepopulate blob cache values round-tripping through Java bytes.
- Ownership tests should verify Java callback objects remain usable when assigned as comparators, merge operators, compaction filters/factories, WAL filters, loggers, event listeners, table filters, and table-property collectors.
- Option behavior tests should open DBs with configured values and observe effects: create-if-missing, missing column-family creation, WAL directories and recovery modes, direct IO/mmap flags, rate limiting, statistics persistence, row cache, compaction options, blob options, prefix extractors, and table/memtable factories.
- Boundary tests should include negative Java values for unsigned native fields, `size_t` overflow checks where implemented, large path target sizes, invalid logger/comparator type bytes, null or disposed native handles, and Java exceptions raised during string or array conversion.

### subset-b-008651: lines 7873-8810

# sources/storage-engines/rocksdb/java/rocksjni/options.cc lines 7873-8810

## Purpose

This chunk implements JNI bridge functions for the tail of `org.rocksdb.DBOptions`, all visible `org.rocksdb.WriteOptions`, `org.rocksdb.ReadOptions`, `org.rocksdb.ComparatorOptions`, and `org.rocksdb.FlushOptions` native methods in this line range. The functions translate Java `long` native handles into RocksDB C++ option objects, allocate/copy/delete those objects, and expose direct setters/getters for option fields used by write, read, comparator callback, and flush operations.

The code is intentionally thin: Java owns a `RocksObject` handle, calls one of these `Java_org_rocksdb_*` symbols, and the native method either mutates a C++ options struct field, returns a field value, or returns a pointer encoded as `jlong` using `GET_CPLUSPLUS_POINTER`.

## Important APIs, Types, and Functions

### DBOptions tail

- `Java_org_rocksdb_DBOptions_setMaxBgErrorResumeCount` and `maxBgerrorResumeCount` map Java `int` to/from `DBOptions::max_bgerror_resume_count`.
- `Java_org_rocksdb_DBOptions_setBgerrorResumeRetryInterval` and `bgerrorResumeRetryInterval` map Java `long` to/from `DBOptions::bgerror_resume_retry_interval` as `uint64_t`.
- `Java_org_rocksdb_DBOptions_setDailyOffpeakTimeUTC` copies a Java UTF string into `DBOptions::daily_offpeak_time_utc`; `dailyOffpeakTimeUTC` returns it as a new Java string.
- The chunk starts at line 7873, so `setMaxBgErrorResumeCount` begins in the previous chunk and is only partially visible here.

### WriteOptions

- `newWriteOptions` allocates `new ROCKSDB_NAMESPACE::WriteOptions`.
- `copyWriteOptions` constructs a shallow C++ copy from another `WriteOptions` handle.
- `disposeInternalJni` deletes the native object after asserting the handle is non-null.
- Field bridge pairs cover:
  - `sync`
  - `disableWAL`
  - `ignore_missing_column_families`
  - `no_slowdown`
  - `low_pri`
  - `memtable_insert_hint_per_batch`

### ReadOptions

- `newReadOptions__` allocates default `ReadOptions`.
- `newReadOptions__ZZ` allocates `ReadOptions(verify_checksums, fill_cache)`.
- `copyReadOptions` shallow-copies the native `ReadOptions`; Java separately keeps references to pointer-backed slice fields.
- `disposeInternalJni` deletes the native object.
- Boolean field bridges cover `verify_checksums`, `fill_cache`, `tailing`, `total_order_seek`, `prefix_same_as_start`, `pin_data`, `background_purge_on_iterator_cleanup`, `ignore_range_deletions`, `auto_prefix_mode`, and `async_io`.
- Numeric and enum bridges cover `readahead_size`, `max_skippable_internal_keys`, `read_tier`, `deadline`, `io_timeout`, and `value_size_soft_limit`.
- Pointer bridges cover:
  - `snapshot`, a `const Snapshot*` assigned from a Java `Snapshot` handle.
  - `iterate_upper_bound` and `iterate_lower_bound`, assigned from `Slice*` handles.
  - `timestamp` and `iter_start_ts`, assigned from `Slice*` handles.
  - `table_filter`, assigned from `TableFilterJniCallback::GetTableFilterFunction()`.

### ComparatorOptions

- `newComparatorOptions` allocates `ComparatorJniCallbackOptions`, not a RocksDB core options type. This struct configures Java comparator callback behavior.
- `reusedSynchronisationType` and `setReusedSynchronisationType` convert between Java byte enum values and C++ `ReusedSynchronisationType` through `ReusedSynchronisationTypeJni` in `portal.h`.
- `useDirectBuffer` and `setUseDirectBuffer` bridge `ComparatorJniCallbackOptions::direct_buffer`.
- `maxReusedBufferSize` and `setMaxReusedBufferSize` bridge `ComparatorJniCallbackOptions::max_reused_buffer_size`.
- `disposeInternalJni` deletes the callback-options object.

### FlushOptions

- `newFlushOptions` allocates `new ROCKSDB_NAMESPACE::FlushOptions`.
- `setWaitForFlush` and `waitForFlush` bridge `FlushOptions::wait`.
- `setAllowWriteStall` and `allowWriteStall` bridge `FlushOptions::allow_write_stall`.
- `disposeInternalJni` deletes the native object.

## Control Flow

The dominant control flow is one JNI call per Java option operation:

1. Java stores a native pointer as `long nativeHandle_`.
2. Java calls a static or instance native method with that handle.
3. C++ casts the `jlong` back to the expected C++ type with `reinterpret_cast`.
4. C++ reads or writes a field, constructs an object, copies an object, deletes an object, or returns a subordinate pointer.
5. Return values are cast back to JNI primitives or `jlong`.

Only a few functions have extra control flow:

- `setDailyOffpeakTimeUTC` calls `GetStringUTFLength` and `GetStringUTFChars`, checks for a pending Java exception, copies the bytes into `std::string`, then releases the UTF chars. If `GetStringUTFChars` fails, the function returns early with the Java exception still pending.
- `setTableFilter` casts the Java table-filter handle to `TableFilterJniCallback*` and stores the callback object's `std::function` into `ReadOptions::table_filter`. Later RocksDB iterator construction invokes that function from core read paths.
- Lifecycle functions assert non-null before `delete`, but otherwise do not validate handle ownership.

## State and Persistence Behavior

The options objects are process-memory state only. This chunk does not write files or persist configuration. Persistence effects happen later when these options are passed into RocksDB operations:

- `WriteOptions::sync` and `disableWAL` directly affect crash durability. `sync=true` requests durable syncing before write completion; `disableWAL=true` skips WAL logging and can lose recent writes after crash unless data is flushed/backed up appropriately.
- `WriteOptions::ignore_missing_column_families`, `no_slowdown`, `low_pri`, and `memtable_insert_hint_per_batch` affect write admission, error behavior, and performance but not on-disk format.
- `ReadOptions` fields affect read consistency, iterator bounds, cache population, IO behavior, and timestamp visibility. Snapshot and slice fields are borrowed pointers, so their Java/C++ lifetime must outlive reads using this `ReadOptions`.
- `FlushOptions::wait` controls whether flush calls block until completion. `allow_write_stall` decides whether a flush may proceed even when it can stall foreground writes.
- `ComparatorOptions` affect Java comparator callback memory and synchronization behavior; they are consumed when constructing comparator callbacks and do not themselves persist.

## Dependencies and Integration Points

This chunk depends on:

- RocksDB public C++ types from `rocksdb/options.h`, including `DBOptions`, `WriteOptions`, `ReadOptions`, and `FlushOptions`.
- `rocksdb/db.h` for `Snapshot` and related DB-facing types.
- `rocksdb/slice.h` transitively for `Slice` pointer fields.
- JNI generated headers such as `include/org_rocksdb_WriteOptions.h`, `include/org_rocksdb_ReadOptions.h`, `include/org_rocksdb_ComparatorOptions.h`, and `include/org_rocksdb_FlushOptions.h`.
- `rocksjni/comparatorjnicallback.h` for `ComparatorJniCallbackOptions`.
- `rocksjni/table_filter_jnicallback.h` for `TableFilterJniCallback`.
- `rocksjni/portal.h` for enum conversion helpers and `GET_CPLUSPLUS_POINTER`.

Java integration points include:

- `java/src/main/java/org/rocksdb/WriteOptions.java`, which calls the write-option allocation, copy, field, and disposal natives.
- `java/src/main/java/org/rocksdb/ReadOptions.java`, which calls the read-option natives and holds Java references to lower/upper bound and timestamp slices so the borrowed native `Slice*` values remain valid.
- `java/src/main/java/org/rocksdb/ComparatorOptions.java`, which exposes comparator callback synchronization and buffer reuse settings.
- `java/src/main/java/org/rocksdb/FlushOptions.java`, which wraps flush option allocation and field access.
- `AbstractTableFilter` and `TableFilterJniCallback`, where Java callback objects are converted into a C++ function stored in `ReadOptions::table_filter`.
- RocksDB operation JNI code elsewhere, such as DB `put`, `write`, `get`, iterator, and flush calls, consumes these option handles by reference.

## Risks and Edge Cases

- Handle casts are unchecked. Passing the wrong native handle type or a disposed handle can corrupt memory or crash the JVM.
- Copy constructors for `WriteOptions` and `ReadOptions` are shallow. For `ReadOptions`, pointer fields such as snapshot and slices are copied as raw pointers; Java tries to retain slice references in its copy constructor, but snapshot and table-filter lifetimes still require caller discipline.
- `ReadOptions::snapshot` returns a borrowed `Snapshot*` encoded as `jlong`; Java wraps it as a `Snapshot` but does not own the DB snapshot lifecycle. Releasing the snapshot while options or iterators still use it is unsafe.
- `iterate_lower_bound`, `iterate_upper_bound`, `timestamp`, and `iter_start_ts` are raw `Slice*` pointers. Java retains references for set values, but returned wrappers are non-owning for bounds; timestamp accessors in Java should be checked carefully for ownership semantics because the native pointer is still owned outside the returned wrapper.
- `setTableFilter` does not null-check the callback handle. Passing null from Java would dereference a null `TableFilterJniCallback*`. The Java method accepts `AbstractTableFilter tableFilter` and immediately accesses `tableFilter.nativeHandle_`, so normal Java calls fail before JNI on null, but native misuse remains unsafe.
- `setDailyOffpeakTimeUTC` does not release UTF chars if an exception is raised after `GetStringUTFChars` but before release; in the visible code, the only checked exception point is immediately after acquisition, before the string copy.
- Several numeric casts can reinterpret negative Java values as large unsigned C++ values, e.g. `bgerror_resume_retry_interval`, `readahead_size`, `max_skippable_internal_keys`, and `value_size_soft_limit`.
- `deadline` and `io_timeout` cast Java `long` through `int64_t` into `std::chrono::microseconds`; negative or overflow-prone inputs are not rejected here.
- The C++ `asyncIo` methods are declared with a `jobject` second parameter and a handle argument, while `ReadOptions.java` declares them as non-static native methods with a single `long` handle. That matches JNI instance-native shape, but differs from the mostly static native pattern in the same class and should be covered by tests.
- `bestEffortsRecovery` just before this chunk returns `static_cast<jlong>` from a `jboolean` function. Although outside the requested start line except for context, it is adjacent enough to be a useful review signal for this region.
- `FlushOptions.java` names its loader helper `newFlushOptionsInance`, a typo that is harmless if consistently referenced, but generated-header or manual binding changes could miss it.

## Test Signals

Useful tests for this chunk are JNI round-trip tests and operation-level behavior tests:

- Construct, copy, mutate, read back, and dispose `WriteOptions`, `ReadOptions`, `ComparatorOptions`, and `FlushOptions` from Java.
- Verify `WriteOptions` defaults and setters for `sync`, `disableWAL`, missing column-family handling, slowdown behavior, low-priority writes, and memtable insert hints.
- Exercise `ReadOptions` with checksums, fill-cache, tailing iterators, total-order seek, prefix-same-as-start, pinning, readahead, max-skippable keys, read tier, deadlines, IO timeout, value soft limit, and async IO.
- Use a live DB snapshot in `ReadOptions`, read through it, release it after use, and assert no stale reads or crashes.
- Use lower and upper bound slices, then let local Java variables go out of scope while `ReadOptions` still exists, confirming the Java retention fields protect native slice pointers.
- Use timestamp and iter-start timestamp slices with a timestamp-aware comparator if the feature is enabled in the test matrix.
- Install an `AbstractTableFilter` on `ReadOptions` and verify iterator table skipping invokes the Java callback and handles callback exceptions as expected.
- Verify `ComparatorOptions` conversion for every `ReusedSynchronisationType`, direct vs heap byte-buffer callbacks, and reused buffer size zero/small/large cases.
- Flush with `wait=true/false` and `allow_write_stall=true/false`, checking API return behavior under write-pressure scenarios.
- Run JNI signature/linkage tests, especially for overloaded `newReadOptions`, instance-style `asyncIo` methods, and the `FlushOptions` allocation path.
