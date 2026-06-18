<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/jni_perf_context.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/jni_perf_context.cc

## Purpose
Exposes RocksDB thread-local `PerfContext` counters to Java through a large set of primitive getters plus reset and string conversion.

## Important APIs and Types
PerfContext Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Every getter casts a `PerfContext*` handle and returns one field as `jlong`; `reset` calls `Reset()`, and `toString` returns the native `ToString()` result as a Java string. Covered fields span block/cache reads, blob reads, skipped internal keys, memtable/output-file timing, write timing, DB mutex waits, table iterator timings, bloom hits/misses, Env operation timings, CPU timings, encryption/decryption, and async seek count.

## State and Persistence Behavior
State is thread/perf-context memory, usually tied to RocksDB perf instrumentation. It is observational and non-persistent.

## Dependencies and Integration Points
Depends on exact `PerfContext` struct fields. Main risk is native/Java drift when fields are added/removed or renamed; this file is mechanically repetitive and easy to miss in upgrades. Tests should enable perf level, perform reads/writes/seeks, verify nonzero expected counters, reset behavior, and `toString` conversion.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/jni_perf_context.cc -->
