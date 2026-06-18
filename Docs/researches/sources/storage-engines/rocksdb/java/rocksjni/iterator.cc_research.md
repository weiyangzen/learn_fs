<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/iterator.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/iterator.cc

## Purpose
Implements Java iterator movement, seeking, status checks, and key/value extraction for byte arrays and direct buffers.

## Important APIs and Types
RocksIterator Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Movement methods cast the handle and call `SeekToFirst`, `SeekToLast`, `Next`, `Prev`, `Refresh`, `Seek`, and `SeekForPrev`. Seek overloads copy Java byte arrays or validate direct buffers via `JniUtil`. `status0Jni` throws on non-OK iterator status. Key/value methods return new byte arrays or copy into caller-provided direct/byte-array buffers and return the full native slice length.

## State and Persistence Behavior
Iterator state is native cursor state over a DB snapshot/read options. It does not persist data but exposes persisted keys/values and can become invalid as DB state changes unless refreshed.

## Dependencies and Integration Points
Depends on `portal.h` and JNI buffer helpers. Risks include reading key/value when invalid, buffer-size truncation semantics, direct buffer validation, exception handling for refresh/status, and iterator use after DB/CF close. Tests should cover all seek/copy overloads, small target buffers, invalid iterator status, and refresh with snapshots.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/iterator.cc -->
