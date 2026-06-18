<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/event_listener.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/event_listener.cc

## Purpose
Creates and disposes Java-backed RocksDB `EventListener` instances.

## Important APIs and Types
AbstractEventListener Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`createNewEventListener` converts an enabled-callback bitset/enum from Java, allocates `EventListenerJniCallback`, wraps it in `std::shared_ptr<EventListener>`, and returns the wrapper pointer. Disposal deletes the heap shared pointer wrapper.

## State and Persistence Behavior
Listeners are long-lived in DB options and observe flush, compaction, file I/O, errors, and recovery. They hold Java references but do not persist state themselves.

## Dependencies and Integration Points
Depends on `event_listener_jnicallback.*` and enabled callback conversion. Risks are callbacks after Java object disposal, thread attachment, and event-method signature drift. Tests should register listeners with selective enabled callbacks and verify callback count/ordering.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/event_listener.cc -->
