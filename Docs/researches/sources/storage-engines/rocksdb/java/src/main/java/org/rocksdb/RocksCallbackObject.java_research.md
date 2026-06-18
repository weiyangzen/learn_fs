# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksCallbackObject.java

## Purpose
`RocksCallbackObject` is the abstract base for Java objects that are represented by native C++ callback adapters. It differs from `RocksObject` because native C++ may call back into Java methods through JNI.

## Important APIs, Types, And Functions
- Field `protected final long nativeHandle_` stores the native callback adapter pointer.
- Constructor accepts optional native parameter handles, marks the object as owning via `AbstractImmutableNativeReference`, and calls subclass `initializeNative(...)`.
- `toNativeHandleList(List<? extends RocksCallbackObject>)` converts nullable Java callback lists to native handle arrays, returning an empty array for null.
- Abstract `initializeNative(long...)` must allocate the appropriate native callback object.
- `disposeInternal()` deletes the native callback through static native `disposeInternal(long)`.

## Control Flow
Subclasses call the base constructor, which immediately delegates to the subclass implementation of `initializeNative`. Later, options or write batches pass callback handles into native RocksDB. When disposed, JNI deletes the pointer as a `ROCKSDB_NAMESPACE::JniCallback*`; the native implementation relies on virtual destructors to clean concrete callback subclasses.

## State And Persistence Behavior
The Java object owns the native callback adapter. Callback state may include global or weak Java references inside native code depending on the subclass. `toNativeHandleList` exposes raw handles without retaining the list; consuming options generally must keep Java callback objects reachable for the native use duration. Callback objects are runtime integration objects and do not persist database data.

## Dependencies And Integration Points
- Extends `AbstractImmutableNativeReference`.
- Subclasses include `AbstractEventListener`, `Logger`, `AbstractTraceWriter`, `AbstractTransactionNotifier`, `AbstractCompactionFilterFactory`, and `WriteBatch.Handler`.
- `Options` and `DBOptions` use `toNativeHandleList` for event listeners.
- JNI implementation is in `java/rocksjni/rocks_callback_object.cc`; callback adapter infrastructure lives under `java/rocksjni/*jnicallback*`.

## Risks And Edge Cases
- The constructor calls an abstract method before subclass construction has finished; subclass `initializeNative` must not depend on uninitialized subclass fields.
- `toNativeHandleList` does not null-check elements; null entries cause `NullPointerException`.
- Native deletion through base `JniCallback*` assumes correct virtual destructors; the JNI file contains a TODO noting this assumption.
- Disposing callback objects while native RocksDB may still invoke them can lead to use-after-free or JVM crashes.

## Test Signals
- Callback behavior is indirectly tested through table filters, event listeners, loggers, transaction notifiers, write-batch handlers, and compaction filter factories.
- Focused lifecycle tests should verify callbacks remain valid while installed in options/DBs and fail predictably when closed too early.
