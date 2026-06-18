<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/rocksdb_exception_test.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/rocksdb_exception_test.cc

Purpose: Native test helper for verifying Java `RocksDBException` construction from strings and C++ `Status` objects.

Important APIs/types/functions: `raiseException` throws with only a message. `raiseExceptionWithStatusCode` and `raiseExceptionNoMsgWithStatusCode` use `Status::NotSupported`. `raiseExceptionWithStatusCodeSubCode` and `raiseExceptionNoMsgWithStatusCodeSubCode` use `Status::TimedOut(kLockTimeout)`. `raiseExceptionWithStatusCodeState` uses `Status::NotSupported(Slice("test state"))`.

Control flow: Each JNI method directly calls `RocksDBExceptionJni::ThrowNew`; no native value is returned. Java tests catch the thrown exception and inspect message, status code, subcode, and state.

State and persistence behavior: No native state is retained and no persistent state is touched.

Dependencies and integration points: Includes generated `org_rocksdb_RocksDBExceptionTest.h`, `rocksdb/status.h`, `rocksdb/slice.h`, and exception conversion helpers from `portal.h`.

Risks: This is test-only surface; production risk is low. Its value depends on staying synchronized with Java exception fields and enum mappings.

Test signals: The file itself is a test signal. Java tests should assert each overload preserves message presence/absence, status code, subcode, and state bytes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/rocksdb_exception_test.cc -->
