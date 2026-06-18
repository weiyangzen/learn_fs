<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/cplusplus_to_java_convert.h -->
# sources/storage-engines/rocksdb/java/rocksjni/cplusplus_to_java_convert.h

## Purpose
Provides the canonical pointer-to-`jlong` macro used throughout RocksJNI.

## Important APIs and Types
C++ pointer conversion helpers. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The header defines `GET_CPLUSPLUS_POINTER` as a `reinterpret_cast<jlong>` of a C++ pointer. It is intentionally small but central to every opaque native handle crossing the JNI boundary.

## State and Persistence Behavior
It stores no state and persists nothing; it defines handle representation for Java-owned native state.

## Dependencies and Integration Points
All bridge files depend on this convention. Risks are portability if pointer width exceeds `jlong`, misuse with non-pointer values, and lack of type safety. Test signal is broad JNI handle construction/disposal coverage on supported architectures.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/cplusplus_to_java_convert.h -->
