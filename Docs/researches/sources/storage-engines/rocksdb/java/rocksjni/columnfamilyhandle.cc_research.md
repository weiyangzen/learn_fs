<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/columnfamilyhandle.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/columnfamilyhandle.cc

## Purpose
Implements Java accessors for a native `ColumnFamilyHandle`: `getName`, `getID`, `getDescriptor`, and disposal.

## Important APIs and Types
ColumnFamilyHandle Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Each accessor casts the opaque handle. `getName` copies the C++ string to a byte array, `getID` returns the 32-bit id, and `getDescriptor` fills a local `ColumnFamilyDescriptor`, constructs the Java descriptor on success, or throws `RocksDBExceptionJni` on failure.

## State and Persistence Behavior
The handle represents live DB column-family state; deletion here releases the native `ColumnFamilyHandle` object but does not delete on-disk column-family data. Descriptor construction snapshots options at call time.

## Dependencies and Integration Points
Depends on `portal.h` converters. Risks are double-free if Java ownership rules are violated, null handles, and descriptor conversion drift as RocksDB options evolve. Test signals include descriptor round trips, close/dispose order, and failure after DB/CF invalidation.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/columnfamilyhandle.cc -->
