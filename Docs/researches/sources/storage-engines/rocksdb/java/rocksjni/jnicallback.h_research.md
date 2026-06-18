<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/jnicallback.h -->
# sources/storage-engines/rocksdb/java/rocksjni/jnicallback.h

## Purpose
Declares the base class shared by RocksJNI callback bridges.

## Important APIs and Types
JniCallback base declaration. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The class stores `JavaVM*` and `jobject m_jcallback_obj`, declares constructor/destructor, and protected `getJniEnv`/`releaseJniEnv` helpers.

## State and Persistence Behavior
State is callback lifetime metadata only; no persistence. The global reference prevents Java callback collection while native RocksDB may invoke it.

## Dependencies and Integration Points
Integration spans comparator, logger, event listener, and compaction filter factory. Risks are subclasses assuming `m_jcallback_obj` is valid after constructor exceptions and lifecycle during JVM shutdown. Compile tests plus callback lifecycle tests are the primary signal.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/jnicallback.h -->
