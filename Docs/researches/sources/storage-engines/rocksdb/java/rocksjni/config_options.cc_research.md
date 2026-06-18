<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/config_options.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/config_options.cc

## Purpose
Wraps `rocksdb::ConfigOptions` for parsing and stringifying RocksDB option configurations.

## Important APIs and Types
ConfigOptions Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
JNI methods allocate/delete `ConfigOptions`, set `env`, delimiter, ignore-unknown-options, input-strings-escaped, and sanity level via `SanityLevelJni`. `setDelimiter` copies a Java string into the native delimiter field.

## State and Persistence Behavior
State is parser configuration only; persistence effects occur when other APIs use it to load/save option strings or files.

## Dependencies and Integration Points
Depends on Env handles and portal enum converters. Risks are dangling `env` pointer if Java disposes the env too early, delimiter encoding surprises, and sanity-level enum drift. Tests should parse option strings with custom delimiter and invalid options.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/config_options.cc -->
