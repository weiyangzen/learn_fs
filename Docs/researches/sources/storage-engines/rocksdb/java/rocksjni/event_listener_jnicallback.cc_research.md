<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/event_listener_jnicallback.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/event_listener_jnicallback.cc

## Purpose
Implements RocksDB event callbacks by dispatching to Java listener methods.

## Important APIs and Types
EventListenerJniCallback implementation. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Constructor caches method IDs for enabled events. Each `On...` method checks enabled flags, prepares Java event info objects through portal converters, attaches the thread, calls the Java method, checks/describes exceptions, and cleans local refs. File I/O completion callbacks share `OnFileOperation`; background error and recovery callbacks can pass mutable status objects back to Java.

## State and Persistence Behavior
State is inherited Java global callback reference plus cached method IDs and enabled-event mask. It observes persisted-file lifecycle events but does not own DB state. Some callbacks run on RocksDB background threads.

## Dependencies and Integration Points
Depends heavily on `portal.h` event-info converters and `JniCallback`. Risks include exception swallowing/printing rather than propagating, local reference leaks under high event volume, callback reentrancy, and mutable status handling in error callbacks. Tests should stress all enabled callback bits, background-thread events, and Java exceptions.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/event_listener_jnicallback.cc -->
