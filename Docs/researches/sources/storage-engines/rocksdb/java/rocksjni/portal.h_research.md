# Research: sources/storage-engines/rocksdb/java/rocksjni/portal.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008653`: lines 1-7632, `Docs/researches/chunks/subset-b-008653_research.md`
- `subset-b-008654`: lines 7633-9355, `Docs/researches/chunks/subset-b-008654_research.md`

## Chunk Research

### subset-b-008653: lines 1-7632

# sources/storage-engines/rocksdb/java/rocksjni/portal.h lines 1-7632

## Scope

This chunk covers the first and largest part of RocksDB's Java JNI portal header. It starts at the file header and includes the common JNI class/method lookup helpers, exception/status conversion, collection and byte/string utilities, native-handle portals for many Java wrapper classes, callback bridge method IDs, metadata object constructors, and a large set of Java/C++ enum mapping helpers. The chunk stops at line 7632 inside `CompactionReasonJni::toJavaCompactionReason()`, immediately after the `kRefitLevel` case label; the rest of that mapping and the remaining portals are in the next chunk.

## Purpose

`portal.h` is the central C++ helper layer used by RocksJNI code to cross the Java/C++ boundary. It caches or retrieves Java classes, method IDs, field IDs, constructors, enum values, and native object handles so JNI implementation files can avoid repeating fragile signature strings and local reference management.

The header also defines bidirectional conversion contracts between Java-visible RocksDB wrapper types and native RocksDB structures. In this chunk those contracts include `Status`, `RocksDBException`, Java arrays and collections, byte buffers, maps, write batch handlers, backup metadata, table properties, column family descriptors, transaction/deadlock objects, thread status, statistics tickers/histograms, compression/compaction/options enums, and several callback interfaces.

This file does not implement RocksDB storage behavior itself. It is glue code that makes Java API behavior line up with C++ RocksDB semantics, including exception propagation, native pointer ownership, enum ordinal stability, direct-buffer access, and metadata object construction.

## Important APIs, Types, and Functions

- `JavaClass::getJClass()` wraps `JNIEnv::FindClass()` and asserts the result. Every portal class builds on this pattern with the Java binary name for its wrapper type.
- `RocksDBNativeClass<PTR, DERIVED>` and `NativeRocksMutableObject<PTR, DERIVED>` are template bases for Java objects that carry native C++ handles. `NativeRocksMutableObject::setHandle()` calls Java `setNativeHandle(long, boolean)` using `GET_CPLUSPLUS_POINTER()`.
- `JavaException<DERIVED>` is the base for `IllegalArgumentExceptionJni`, `OutOfMemoryErrorJni`, and `RocksDBExceptionJni`. It centralizes `ThrowNew()` and reports unexpected class/constructor failures to `std::cerr`.
- `CodeJni`, `SubCodeJni`, and `StatusJni` translate between `org.rocksdb.Status`, `Status.Code`, `Status.SubCode`, and `ROCKSDB_NAMESPACE::Status`. `StatusJni::construct()` creates a Java `Status`; `StatusJni::toCppStatus()` reconstructs a native `Status` from Java code/subcode values.
- `RocksDBExceptionJni` constructs and throws Java `RocksDBException` from a native `Status`, either with only status or with a message plus status. It can also extract a native `Status` from a caught Java exception via `getStatus()`.
- `ListJni`, `MapJni`, and `HashMapJni` provide Java collection portals. `HashMapJni::fromCppMap()` converts C++ maps with string, `uint32_t`, or `uint64_t` values into Java `HashMap` instances using `String`, `Integer`, and `Long` wrappers.
- `ByteJni`, `ByteBufferJni`, `IntegerJni`, `LongJni`, and `StringBuilderJni` wrap common JDK types. `ByteBufferJni::constructWith()` can create direct buffers backed by C++ memory or heap `ByteBuffer`s filled from a C++ buffer.
- `JniUtil` is the main utility class. It attaches/detaches native threads to the JVM, copies strings and bytes between Java and C++, creates Java arrays with size checks, converts `byte[][]` to C++ strings through callback functions, performs array/direct-buffer key/value operations, converts arrays of native pointers, and copies C++ data into direct buffers.
- Native wrapper portals include `RocksDBJni`, `OptionsJni`, `DBOptionsJni`, `ColumnFamilyOptionsJni`, `WriteOptionsJni`, `ReadOptionsJni`, `WriteBatchJni`, `WriteBatchWithIndexJni`, `BackupEngineOptionsJni`, `BackupEngineJni`, `IteratorJni`, `FilterPolicyJni`, `ColumnFamilyHandleJni`, `FlushOptionsJni`, and `ComparatorOptionsJni`.
- `WriteBatchHandlerJni` exposes all Java `WriteBatch.Handler` callbacks needed by native batch iteration: put, merge, delete, single delete, delete range, log data, blob index put, transaction prepare/commit/rollback markers, no-op markers, timestamped commit markers, and `shouldContinue()`.
- Callback bridge portals include `AbstractCompactionFilterFactoryJni`, `AbstractTransactionNotifierJni`, `AbstractComparatorJniBridge`, `AbstractComparatorJni`, `LoggerJni`, and `AbstractTableFilterJni`. They expose Java callback method IDs consumed by C++ callback adapter classes included at the top of the file.
- Object construction portals include `ColumnFamilyOptionsJni::construct()`, `WriteBatchJni::construct()`, `WriteBatchSavePointJni::construct()`, `BackupInfoJni::construct0()`, `BackupInfoListJni::getBackupInfo()`, `BatchResultJni::construct()`, `TransactionJni::newWaitingTransactions()`, `TransactionDBJni::newDeadlockInfo()`, `KeyLockInfoJni::construct()`, `DeadlockPathJni::construct()`, `TablePropertiesJni::fromCppTableProperties()`, `ColumnFamilyDescriptorJni::construct()`, and `ThreadStatusJni::construct()`.
- Enum mapping classes in this chunk include `FilterPolicyTypeJni`, `WriteTypeJni`, `BottommostLevelCompactionJni`, `CompactionStopStyleJni`, `CompressionTypeJni`, `CompactionPriorityJni`, `WALRecoveryModeJni`, `TickerTypeJni`, `HistogramTypeJni`, `StatsLevelJni`, `RateLimiterModeJni`, `MemoryUsageTypeJni`, `PerfLevelTypeJni`, `TxnDBWritePolicyJni`, `IndexTypeJni`, `DataBlockIndexTypeJni`, `IndexSearchTypeJni`, `ChecksumTypeJni`, `IndexShorteningModeJni`, `PriorityJni`, `ThreadTypeJni`, `OperationTypeJni`, `OperationStageJni`, `StateTypeJni`, `CompactionStyleJni`, and the beginning of `CompactionReasonJni`.

## Control Flow

The common portal flow is: find the Java class, retrieve a method/field/constructor ID with a literal JNI signature, call the Java method or construct the object, check `ExceptionCheck()`, clean up local references, and return either the Java reference/value or `nullptr`/a boolean error signal.

Exception flow is explicit. Simple Java exceptions use `JavaException::ThrowNew()`. `RocksDBExceptionJni` is more involved: it finds the Java exception class, gets the constructor accepting a `Status` or `(String, Status)`, builds a Java `Status` through `StatusJni::construct()`, creates a `jthrowable`, calls `Throw()`, then deletes local references. If any JNI step fails, the function leaves the pending Java exception intact and returns true when an exception is pending.

Status conversion is bidirectional. Native-to-Java conversion maps C++ `Status::Code` and `Status::SubCode` to stable byte values, copies the optional state string with `NewStringUTF()`, and invokes the Java `Status(byte, byte, String)` constructor. Java-to-native conversion calls `getCode()`, `getSubCode()`, each enum's `getValue()`, and `getState()`, then uses `StatusJni::toCppStatus(jbyte, jbyte)` to construct an equivalent native status. The current chunk reads the Java state object but does not use its contents when building the native `Status`, so only code/subcode semantics are restored here.

Data-copy control flow in `JniUtil` carefully selects JNI array APIs based on use case. `copyStrings()` iterates a Java `String[]`, gets UTF chars, copies into `std::string`, releases UTF chars, and deletes local refs. `stringsBytes()` builds a Java `byte[][]` by allocating each byte array, writing with `SetByteArrayRegion()`, installing it into the object array, and releasing local refs. `byteString()` and `byteStrings()` use `GetByteArrayElements()` and release with `JNI_ABORT` because the C++ code only reads. `kv_op()`, `k_op()`, and `v_op()` wrap common byte-array-to-`Slice` flows for write batch and lookup helpers.

Direct-buffer helpers avoid copying but validate buffer shape before creating a `Slice`. `kv_op_direct()`, `k_op_direct()`, and `copyToDirect()` call `GetDirectBufferAddress()` and check `GetDirectBufferCapacity()` against offset plus length. Invalid direct-buffer arguments become Java `RocksDBException`s rather than native crashes.

Object construction helpers follow the same pattern: locate class and constructor, convert dependent fields, construct the Java object, and delete temporary local references on error paths. `TablePropertiesJni::fromCppTableProperties()` is the broadest example, converting numeric fields, byte-array column family name, optional string fields, and two C++ string maps before calling a long Java constructor.

Enum helpers are almost entirely switch statements. They map C++ enum constants to stable Java `jbyte` or `jint` values and, where needed, map those Java values back to C++ defaults. Several mappings reserve or pin values for compatibility, especially `TickerTypeJni` and `HistogramTypeJni`, where the Java representation is a signed byte and newer RocksDB enum values are assigned negative byte values.

## State and Persistence Behavior

The file itself has no persistent storage. Its "state" is JNI lookup state cached in function-local `static jmethodID` or `static jfieldID` variables and, in one template path, a function-local `static jclass`. These caches are process-local and persist for the lifetime of the native library.

Native pointer state is represented as Java `long` values. Portal classes pass pointers through `GET_CPLUSPLUS_POINTER()` and Java constructors such as `<init>(J)V`; Java-side wrappers are expected to store and eventually release or ignore those handles according to their ownership flag. `NativeRocksMutableObject::setHandle()` explicitly includes a `java_owns_handle` boolean to tell Java whether it manages native lifetime.

Memory ownership is mixed and must be respected by callers. `ColumnFamilyOptionsJni::construct()` allocates a fresh native `ColumnFamilyOptions` copy and passes ownership to Java through the native handle. `BatchResultJni::construct()` releases ownership from `batch_result.writeBatchPtr` after constructing the Java object, transferring the write batch pointer to Java. `ByteBufferJni::constructWith(direct=true, buf=nullptr)` allocates a new `char[]` and wraps it in a direct `ByteBuffer`; this depends on the corresponding Java/direct-buffer lifecycle elsewhere to avoid leaking the native allocation.

Local JNI references are short-lived and manually deleted in many paths, especially when loops build Java collections or when constructors allocate multiple intermediate strings/arrays. Some successful construction paths intentionally leave returned local refs alive for the caller, while temporary refs are generally deleted on error. A few successful paths do not delete every temporary ref in this chunk, which is tolerable for small calls but risky in large loops.

The enum byte values are part of the Java API persistence/compatibility surface. `TickerTypeJni` and `HistogramTypeJni` comments explicitly pin values across releases, including reserved max enum values and skipped byte slots. Changing these mappings would break serialized/configured Java clients or cross-version assumptions even though the code is not writing persistent files itself.

## Dependencies and Integration Points

- JNI core: `jni.h`, `JNIEnv`, `JavaVM`, `jclass`, `jmethodID`, `jfieldID`, `jobject`, primitive arrays, direct buffers, local refs, pending exceptions, and thread attachment APIs.
- RocksDB public C++ APIs: `rocksdb/db.h`, `status.h`, `table.h`, `filter_policy.h`, `perf_level.h`, `rate_limiter.h`, backup engine, memory util, transaction DB, and write batch with index.
- RocksJNI callback adapters: `compaction_filter_factory_jnicallback.h`, `comparatorjnicallback.h`, `event_listener_jnicallback.h`, `loggerjnicallback.h`, `table_filter_jnicallback.h`, `trace_writer_jnicallback.h`, `transaction_notifier_jnicallback.h`, `wal_filter_jnicallback.h`, and `writebatchhandlerjnicallback.h`.
- Java RocksDB classes: the code assumes exact class names under `org/rocksdb`, including nested classes such as `Status$Code`, `WriteBatch$Handler`, `TransactionLogIterator$BatchResult`, `TransactionDB$DeadlockInfo`, and `WBWIRocksIterator$WriteType`.
- Java standard library integration: `java/lang/String`, `StringBuilder`, boxed numeric wrappers, exceptions, `java/util/List`, `Iterator`, `ArrayList`, `Map`, `HashMap`, and `java/nio/ByteBuffer`.
- Native implementation files include this header to obtain method IDs and conversion helpers while implementing JNI entry points for RocksDB, options, iterators, write batches, transactions, backup, statistics, and callbacks.

## Risks and Edge Cases

- Most method and field IDs are found by literal JNI signatures. Any Java method rename, signature change, nested-class rename, or constructor reorder breaks native code at runtime.
- `JavaClass::getJClass()` asserts non-null after `FindClass()`. In release builds without assertions, callers still depend on subsequent null checks; in debug builds, a class-loading issue can abort rather than propagate cleanly.
- JNI local reference cleanup is inconsistent in some success paths. Repeated construction of backup info, table properties, or transaction objects in large loops can pressure the local reference table if callers do not manage frames or if temporary refs are not deleted.
- `StatusJni::toCppStatus(JNIEnv*, jobject)` obtains `jstate` but does not copy the state string into the constructed native `Status`, so round-tripping Java status state through this path loses detail beyond code/subcode.
- `JniUtil::check_if_jlong_fits_size_t()` casts `jlong` to `uint64_t`; negative Java values become huge and fail the size check, which is likely intentional for sizes but important for callers expecting signed semantics.
- `JniUtil::k_op_region()` attempts `FindClass("/lang/java/OutOfMemoryError")`, which looks like an invalid Java class name compared with `java/lang/OutOfMemoryError`. If allocation ever fails here, exception construction may not behave as intended.
- `ByteBufferJni::constructWith(direct=true)` can allocate native memory and hand it to `NewDirectByteBuffer()` without a visible deallocation path in this chunk. The matching Java/native cleanup contract must be verified in callers.
- Direct-buffer helpers validate capacity against `offset + length` without explicitly checking negative offsets or lengths before arithmetic. JNI callers should validate Java arguments before using these helpers.
- `KeyLockInfoJni::construct()` allocates a `jlongArray` sized to transaction IDs but does not populate it in this chunk; Java may see an all-zero ID array unless another path fills it.
- `DeadlockPathJni::construct()` requests constructor signature `"([LDeadlockInfo;Z)V"`, which lacks the full package/binary class name normally required for object arrays. That is a high-risk signature if not matched by JNI resolution behavior elsewhere.
- `FilterPolicyJni::getFilterPolicyType()` recognizes `"rocksdb.BuiltinBloomFilter"` but the enum includes `kRibbonFilterPolicy`; ribbon policy detection is not present in this chunk.
- Enum mappings use default fallbacks rather than throwing for unknown values. That preserves compatibility but can silently turn bad Java values into valid RocksDB defaults, changing behavior without a visible error.
- `TickerTypeJni` uses signed `jbyte` values and negative constants for many newer tickers. Java enum value code and tests must preserve signed-byte semantics exactly.
- The chunk ends in the middle of `CompactionReasonJni::toJavaCompactionReason()`, so this report cannot validate the complete compaction-reason mapping. The following chunk must confirm the rest of the cases and the reverse conversion.

## Test Signals

- Java/C++ class signature tests should instantiate every portal-backed Java class and call JNI paths that resolve each cached method, field, and constructor. This catches stale literal signatures.
- Status and exception tests should verify all `Status::Code` and `Status::SubCode` values round-trip to Java and back, including unknown/default behavior and `RocksDBException.getStatus()` extraction.
- Error-path tests should simulate Java allocation failures or pending exceptions around string, array, and object construction to verify local refs are cleaned and pending exceptions are preserved.
- Byte conversion tests should cover empty arrays, large arrays near Java array limits, `byte[][]`, UTF strings, null or empty optional strings, and `Slice` values containing embedded zero bytes.
- Direct-buffer tests should cover valid direct buffers, non-direct buffers, too-small capacities, nonzero offsets, negative Java arguments after entry-point validation, and `copyToDirect()` truncation semantics.
- Native-handle tests should verify Java ownership flags, pointer transfer through constructors, `BatchResultJni` write batch ownership release, and `ColumnFamilyOptionsJni` copy ownership.
- Collection conversion tests should check `HashMapJni::fromCppMap()` for string/string, string/int, string/long, and int/long maps, including null treatment for empty values.
- Callback tests should exercise Java compaction filter factory, transaction notifier, comparator bridge methods, table filter, logger, and write batch handler callbacks from native code.
- Metadata construction tests should validate `BackupInfo`, `WriteBatch.SavePoint`, `TableProperties`, `ColumnFamilyDescriptor`, `ThreadStatus`, waiting transaction, deadlock info/path, and key lock info fields visible on the Java side.
- Enum tests should assert every Java enum value maps to the intended C++ enum and back for compression, compaction, WAL recovery, stats, rate limiter, memory usage, perf level, transaction policy, table options, thread status, ticker, and histogram mappings.
- Compatibility tests should pin `TickerTypeJni` and `HistogramTypeJni` byte values, especially negative ticker values, reserved max values, and skipped histogram slots.
- Boundary tests for this chunk should ensure `CompactionStyleJni` is complete and should be paired with the next chunk's tests for the complete `CompactionReasonJni` mapping.

### subset-b-008654: lines 7633-9355

# sources/storage-engines/rocksdb/java/rocksjni/portal.h lines 7633-9355

## Scope

This chunk covers the tail of RocksJava's JNI portal header. It starts inside `CompactionReasonJni`'s Java-to-C++ mapping and then defines portal helpers for WAL file types, log/live/SST/level/column-family metadata objects, trace writers, WAL filters, WAL processing options, reused synchronization/config sanity/blob-cache enums, enabled event callback masks, event-listener method IDs, event payload wrappers, compact-range timestamps, and reconstruction of Java `BlockBasedTableConfig` from native `BlockBasedTableOptions`.

The code is mostly bridge code: it does not implement RocksDB storage algorithms directly, but it is on the boundary where C++ state, persistent metadata, background-event information, and table options become Java objects or Java callback invocations.

## Purpose

- Keep Java enum byte values synchronized with native RocksDB enum values used by compaction reasons, WAL file types, WAL replay decisions, synchronization strategy, config sanity checks, and blob-cache prepopulation.
- Convert native metadata structs into immutable Java-facing value objects for logs, live files, SST files, levels, column families, flush jobs, table-file creation/deletion, external ingestion, memtable sealing, write stalls, file IO, and compact-range timestamp spans.
- Cache JNI class and method lookup results for callback-heavy paths such as trace writing, WAL filtering, event listener callbacks, and table option reconstruction.
- Expose C++ callback implementations to Java subclasses of `AbstractTraceWriter`, `AbstractWalFilter`, and `AbstractEventListener` through `RocksDBNativeClass` pointer-handle helpers.
- Preserve important storage/persistence details across the Java boundary, including WAL file identity and type, LSM file levels and sequence-number ranges, checksums, table properties, status objects, background-error reasons, and block-based table format/cache/filter settings.

## Important APIs, Types, And Functions

- `CompactionReasonJni::toCppCompactionReason()` maps Java `org.rocksdb.CompactionReason` bytes to native `CompactionReason`, defaulting unknown bytes to `kUnknown`. This chunk includes values through forced blob GC, round-robin TTL, and refit-level compactions.
- `WalFileTypeJni` maps native `WalFileType::{kArchivedLogFile,kAliveLogFile}` to Java bytes and back; unknown Java input defaults to alive log files.
- `LogFileJni::fromCppLogFile()` creates `org.rocksdb.LogFile` from `LogFile::PathName()`, `LogNumber()`, `Type()`, `StartSequence()`, and `SizeFileBytes()`.
- `LiveFileMetaDataJni::fromCppLiveFileMetaData()` converts `LiveFileMetaData` into Java `LiveFileMetaData`, including column-family bytes, level, file name, DB path, size, sequence bounds, smallest/largest keys, sampled reads, compaction flag, entry/delete counts, and file checksum.
- `SstFileMetaDataJni::fromCppSstFileMetaData()` is the non-column-family variant for Java `SstFileMetaData`, carrying file/path strings, size, sequence bounds, key bounds, sampled reads, compaction flag, entry/delete counts, and checksum.
- `LevelMetaDataJni::fromCppLevelMetaData()` builds an array of Java `SstFileMetaData` for every file in a native level and wraps it in `org.rocksdb.LevelMetaData`.
- `ColumnFamilyMetaDataJni::fromCppColumnFamilyMetaData()` builds Java `ColumnFamilyMetaData` from total size, file count, CF name bytes, and an array of `LevelMetaData`.
- `AbstractTraceWriterJni` resolves `AbstractTraceWriter` methods `writeProxy(long)`, `closeWriterProxy()`, and `getFileSize()` for native trace-writer callbacks.
- `AbstractWalFilterJni` resolves `AbstractWalFilter` methods `columnFamilyLogNumberMap(Map, Map)`, `logRecordFoundProxy(long,String,long,long)`, and `name()` for WAL replay filtering.
- `WalProcessingOptionJni` maps Java replay actions to `WalFilter::WalProcessingOption`: continue, ignore current record, stop replay, or mark corrupted. Unknown Java input defaults to `kCorruptedRecord`.
- `ReusedSynchronisationTypeJni`, `SanityLevelJni`, and `PrepopulateBlobCacheJni` translate smaller configuration enums used by Java options/configuration APIs.
- `EnabledEventCallbackJni::toCppEnabledEventCallbacks()` decodes a Java bitmask into a `std::set<EnabledEventCallback>` by scanning `NUM_ENABLED_EVENT_CALLBACK` bits.
- `AbstractEventListenerJni` resolves method IDs for all Java event callbacks in this range: flush begin/completed, table-file deletion/creation/creation-started, compaction begin/completed, memtable sealed, CF handle deletion, external file ingestion, background error, write stall changes, file IO operation completions, file-IO notification opt-in, error recovery begin, and error recovery completed.
- `FlushJobInfoJni`, `TableFileDeletionInfoJni`, `TableFileCreationInfoJni`, `TableFileCreationBriefInfoJni`, `MemTableInfoJni`, `ExternalFileIngestionInfoJni`, `WriteStallInfoJni`, and `FileOperationInfoJni` construct Java event payloads from native event structs.
- `CompactionJobInfoJni::fromCppCompactionJobInfo()` creates Java `CompactionJobInfo` with a raw native pointer handle instead of eagerly copying all fields.
- `CompactRangeOptionsTimestampJni::fromCppTimestamp()` wraps a native `start` and `range` pair into Java `CompactRangeOptions.Timestamp`.
- `BlockBasedTableOptionsJni::construct()` creates Java `BlockBasedTableConfig` from native `BlockBasedTableOptions`, including cache/index/filter booleans, index and checksum enum translations, block sizes/restarts, format version, key-value separation, compression/index-search settings, super-block alignment settings, and filter-policy type/handle.

## Control Flow

Most conversion helpers follow the same JNI pattern. They first resolve the Java class with `JavaClass::getJClass()` or `RocksDBNativeClass::getJClass()`, then resolve a constructor or method signature with `GetMethodID()`, convert native strings/slices/status/table-properties to Java objects, call `NewObject()` or return a cached method ID, and clean up local references on error paths.

Nested metadata conversion is bottom-up. `SstFileMetaDataJni` converts one native SST metadata entry. `LevelMetaDataJni` allocates a Java object array sized to `level_meta_data->files`, fills it by repeatedly calling `SstFileMetaDataJni::fromCppSstFileMetaData()`, and then creates one Java level object. `ColumnFamilyMetaDataJni` repeats the same pattern for levels before constructing the column-family metadata object.

Event-listener dispatch is split between method-ID portals and payload portals. `AbstractEventListenerJni` only looks up Java callback method IDs and their exact signatures. Separate payload classes create the Java argument objects passed to those callbacks, for example `FlushJobInfoJni` for `onFlushBeginProxy`/`onFlushCompletedProxy`, `TableFileCreationInfoJni` for `onTableFileCreated`, and `FileOperationInfoJni` for file IO completion callbacks.

Enum conversion uses explicit `switch` statements over Java byte constants or C++ enum values. Undefined native enum values usually map to `0x7F` or `-0x01` for Java "unknown"; undefined Java enum bytes map to conservative native defaults such as `kUnknown`, `kAliveLogFile`, `kCorruptedRecord`, `ADAPTIVE_MUTEX`, `kSanityLevelExactMatch`, or `kDisable`.

`BlockBasedTableOptionsJni::construct()` has a longer flow. It resolves `BlockBasedTableConfig`'s large constructor signature, detects the native filter policy by compatibility name, exposes the native filter-policy pointer only for recognized built-in policy types, and then passes all supported table-option fields in constructor order.

## State And Persistence Behavior

- This header does not persist data itself; it preserves persisted or runtime RocksDB state when presenting it to Java.
- WAL state crosses the bridge through `LogFileJni` and `WalFileTypeJni`: Java receives the WAL path, log number, alive/archive classification, start sequence, and size.
- Live-file and SST metadata expose LSM persistence state to Java, including levels, file paths, sizes, key bounds, sequence-number bounds, entry/delete counts, compaction state, and checksums.
- Column-family metadata preserves the hierarchy `ColumnFamilyMetaData -> LevelMetaData[] -> SstFileMetaData[]`, matching the source tree's LSM layout rather than flattening it.
- Flush/table-file/external-ingestion event payloads carry persisted-file identities, table properties, global sequence numbers, statuses, job IDs, reasons, and file sizes that Java listeners can use for audit or monitoring.
- File-operation payloads expose path, offset, length, start timestamp, duration, and status, which are observability state from RocksDB's environment/file-system layer.
- `CompactionJobInfoJni` intentionally passes a native pointer handle to Java, so the lifetime of the pointed-to native `CompactionJobInfo` is part of the callback contract.
- `BlockBasedTableOptionsJni::construct()` serializes native block-table configuration into Java configuration state, including filter-policy pointer handles for recognized policies. The resulting Java object is a mirror of native options, not an owner of storage-engine state.

## Dependencies And Integration Points

- JNI dependencies include `JNIEnv`, `jclass`, `jmethodID`, `jobject`, `jobjectArray`, `jstring`, `jbyteArray`, primitive JNI casts, local-reference cleanup, `ExceptionCheck()`, `GetMethodID()`, `NewObject()`, and `NewObjectArray()`.
- Portal base classes are `JavaClass` and `RocksDBNativeClass`, with native-pointer exposure through `GET_CPLUSPLUS_POINTER`.
- Utility dependencies include `JniUtil::toJavaString()`, `JniUtil::copyBytes()`, `StatusJni::construct()`, `TablePropertiesJni::fromCppTableProperties()`, and enum helpers such as `IndexTypeJni`, `DataBlockIndexTypeJni`, `ChecksumTypeJni`, `IndexShorteningModeJni`, `IndexSearchTypeJni`, and `FilterPolicyJni`.
- Native RocksDB types bridged here include `LogFile`, `LiveFileMetaData`, `SstFileMetaData`, `LevelMetaData`, `ColumnFamilyMetaData`, `TraceWriterJniCallback`, `WalFilterJniCallback`, `EventListenerJniCallback`, `FlushJobInfo`, `TableFileDeletionInfo`, `CompactionJobInfo`, `TableFileCreationInfo`, `TableFileCreationBriefInfo`, `MemTableInfo`, `ExternalFileIngestionInfo`, `WriteStallInfo`, `FileOperationInfo`, `BlockBasedTableOptions`, and several RocksDB enums.
- Java classes integrated by exact name/signature include `org.rocksdb.LogFile`, `LiveFileMetaData`, `SstFileMetaData`, `LevelMetaData`, `ColumnFamilyMetaData`, `AbstractTraceWriter`, `AbstractWalFilter`, `AbstractEventListener`, event info classes, `CompactRangeOptions$Timestamp`, and `BlockBasedTableConfig`.
- The callback portals are used by native callback adapter implementations outside this range. Those adapters call the cached `jmethodID`s and payload constructors when RocksDB emits flush, compaction, file IO, WAL replay, trace-writing, or error-recovery events.

## Risks And Edge Cases

- Constructor and method descriptors are hard-coded. Any Java signature change must be mirrored here exactly or runtime `NoSuchMethodError`/assert failures will occur.
- Several methods use `assert(mid != nullptr)` or `assert(jclazz != nullptr)` after lookup. In release builds, a missing method may produce a null method ID that is used later if the assertion is compiled out.
- Local-reference cleanup is inconsistent. Many error paths delete earlier local references, but some successful object-construction paths return without deleting all local refs, relying on JNI frame cleanup. Callback-heavy code should avoid creating excessive local references.
- `FlushJobInfoJni::fromCppFlushJobInfo()` deletes `jfile_path` instead of `jcf_name` when file-path string creation reports an exception. That appears suspicious because `jfile_path` may not be a valid local reference on that path.
- `TableFileDeletionInfoJni::fromCppTableFileDeletionInfo()` creates the file-path Java string inline in `NewObject()` and does not separately check conversion failure or delete the local reference.
- `SstFileMetaDataJni` casts `smallest_seqno` to `jint` while the constructor descriptor expects a `J` long slot. If the native field can exceed 32 bits, Java metadata can be truncated or the varargs call can be ABI-sensitive.
- Enum byte values are a compatibility contract with Java enums. Adding a native enum without updating Java and these switches can silently produce Java "undefined" or default to a potentially wrong native behavior.
- Unknown WAL processing options default to `kCorruptedRecord`, which is fail-closed for replay but can change recovery behavior if Java emits an invalid byte.
- `EnabledEventCallbackJni` shifts `1ULL << i`; correctness depends on `NUM_ENABLED_EVENT_CALLBACK` staying within the width of `jlong`/64-bit masks and Java using the same bit ordering.
- `CompactionJobInfoJni` exposes a native pointer rather than copying fields. Java code must not retain or use it beyond the valid native callback lifetime.
- `BlockBasedTableOptionsJni::construct()` exposes a filter-policy handle only when the compatibility name is recognized. Unknown/custom policies are represented as unknown with handle `0`, which can lose detail when mirroring options to Java.
- `super_block_alignment_space_overhead_ratio` is cast to `jlong` even though the Java constructor slot in the descriptor is `J` and the native option name suggests a ratio; if the native type is non-integral, this conversion deserves scrutiny.

## Test Signals

- RocksJava JNI build/tests should fail quickly if any hard-coded Java constructor or callback method descriptor in this chunk diverges from the corresponding Java class.
- Metadata API tests should check that `getSortedWalFiles`, live-file metadata, SST metadata, level metadata, and column-family metadata expose names, paths, sequence numbers, levels, sizes, checksums, and array nesting accurately.
- Event-listener tests should cover every method ID in `AbstractEventListenerJni`: flush begin/completed, compaction begin/completed, table-file created/deleted/creation-started, memtable sealed, CF handle deletion, external file ingestion, background error, stall changes, file IO completion methods, file-IO opt-in, and error recovery callbacks.
- WAL-filter tests should validate `columnFamilyLogNumberMap`, `logRecordFoundProxy`, callback naming, and all `WalProcessingOption` outcomes: continue, ignore, stop replay, and corrupted record.
- Enum round-trip tests are useful for `CompactionReason`, `WalFileType`, `WalProcessingOption`, `ReusedSynchronisationType`, `SanityLevel`, and `PrepopulateBlobCache`, including undefined-byte behavior.
- Block-based table config tests should compare Java configs constructed from native `BlockBasedTableOptions` against expected cache, block size, checksum, index, filter-policy, format-version, compression, and alignment settings.
- Stress or callback-frequency tests should watch for local-reference table growth and pending Java exceptions in event payload conversion paths.
- Boundary tests should include large sequence numbers for `SstFileMetaData`, custom filter policies in `BlockBasedTableOptions`, invalid enabled-event bitmasks, and Java callbacks throwing exceptions during native event delivery.
