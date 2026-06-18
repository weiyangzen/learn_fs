<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/loggerjnicallback.h -->
# sources/storage-engines/rocksdb/java/rocksjni/loggerjnicallback.h

## Purpose
Declares the Java-backed RocksDB logger class.

## Important APIs and Types
LoggerJniCallback declaration. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The class derives from `JniCallback` and `Logger`, exposes `GetInfoLogLevel`/`SetInfoLogLevel`, overrides both `Logv` variants, and stores method id plus global refs for Java level enums. A private `format_str` helper builds log messages.

## State and Persistence Behavior
State is logger threshold and cached Java references. No persistence unless Java callback stores messages.

## Dependencies and Integration Points
Integration is with DBOptions logger configuration and `loggerjnicallback.cc`. Risks are method/enum signature drift and inherited callback lifecycle. Tests should compile against Java generated headers and exercise native logging through DB open/write/read paths.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/loggerjnicallback.h -->
