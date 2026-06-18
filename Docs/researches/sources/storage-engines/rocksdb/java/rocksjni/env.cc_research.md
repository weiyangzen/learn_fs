<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/env.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/env.cc

## Purpose
Exposes RocksDB `Env` operations and env wrappers to Java: default env, background thread controls, thread list, memory env, and timed env.

## Important APIs and Types
Env Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Default env returns `Env::Default()` without ownership. `RocksEnv.disposeInternal` deletes only non-default/env wrappers. Thread methods cast priority enums and call background-thread APIs. `getThreadList` fills a vector of `ThreadStatus`, builds a Java array, and throws on non-OK status. `RocksMemEnv` and `TimedEnv` allocate wrapper envs and delete them on dispose.

## State and Persistence Behavior
Env state governs filesystem and background execution. Memory env stores file contents in process memory; timed env wraps another env for timing instrumentation. Persistent behavior is indirect through all DB file I/O.

## Dependencies and Integration Points
Depends on Env APIs, memory/timed env utilities, `ThreadStatusJni`, and priority converters. Risks include deleting an env still used by DB/options, treating default env as owned, thread-list local refs/OOM, and wrapper env lifetimes tied to base env. Tests should cover default vs wrapper disposal and thread status retrieval.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/env.cc -->
