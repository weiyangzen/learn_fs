<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/memtablejni.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/memtablejni.cc

## Purpose
Creates native `MemTableRepFactory` implementations from Java memtable configuration classes.

## Important APIs and Types
MemTable factory Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Provides constructors for hash skip list, hash linked list, vector, and skip list factories. Each checks Java `long` values fit in `size_t` before allocation, throws `IllegalArgumentExceptionJni` on overflow, and returns raw factory pointers for options ownership.

## State and Persistence Behavior
Factories are in-memory configuration objects used by column-family options; they influence memtable structure for future writes and flushes. Persistent effects are indirect through memtable flush output ordering/performance.

## Dependencies and Integration Points
Depends on `rocksdb/memtablerep.h` and size-check helpers. Risks include ownership transfer clarity, unsupported factory combinations, and parameter range overflow. Tests should create each factory, open DBs with them, and cover overflow exception paths.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/memtablejni.cc -->
