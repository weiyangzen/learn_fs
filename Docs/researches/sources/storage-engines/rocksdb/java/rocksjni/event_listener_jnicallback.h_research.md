<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/event_listener_jnicallback.h -->
# sources/storage-engines/rocksdb/java/rocksjni/event_listener_jnicallback.h

## Purpose
Defines the enabled callback bit flags and C++ listener class that bridges RocksDB events to Java.

## Important APIs and Types
EventListenerJniCallback declarations. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The header enumerates callback bits for flush, table file events, compaction, memtable, CF deletion, ingestion, background errors, stalls, file I/O, and recovery. The class declares overrides for all corresponding `EventListener` hooks plus helper methods for method-ID initialization and callback setup/cleanup.

## State and Persistence Behavior
State is the enabled mask and cached Java method IDs. No persistence, but listener decisions can influence error recovery if Java mutates status in supported callbacks.

## Dependencies and Integration Points
Integration is with `event_listener.cc` and RocksDB DBOptions listeners. Risks are bitmask drift with Java constants and missing method IDs for newly added events. Tests should compile against every declared override and verify disabled events do not call Java.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/event_listener_jnicallback.h -->
