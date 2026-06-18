# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractCompactionFilterFactory.java

## Purpose
This Java base class lets users implement compaction filter factories in Java while native RocksDB requests new filter instances for individual compactions.

## Important APIs, Types, and Functions
`AbstractCompactionFilterFactory<T extends AbstractCompactionFilter<?>>` extends `RocksCallbackObject`. It has a public constructor, `initializeNative`, private JNI-called `createCompactionFilter(boolean fullCompaction, boolean manualCompaction)`, abstract `createCompactionFilter(Context)`, abstract `name`, custom `disposeInternal`, and native methods `createNewCompactionFilterFactory0` and static `disposeInternal(long)`.

## Control Flow
Construction starts with a zero native handle and initialization creates the native factory callback. When C++ needs a filter, JNI calls the private `createCompactionFilter` method, which builds a `Context`, calls the user's abstract factory method, disowns the returned filter's native handle because C++ takes ownership through `unique_ptr`, and returns the native handle.

## State and Persistence Behavior
The factory owns a native callback wrapper, while individual filters are transferred to C++ ownership. Compaction filters created by the factory can affect persistent key/value retention or modification during compaction, but the factory itself stores no persistent data.

## Dependencies and Integration Points
It integrates with `RocksCallbackObject`, `AbstractCompactionFilter`, native `compaction_filter_factory_jnicallback.cc`, and options APIs that configure compaction filters.

## Risks and Edge Cases
The private JNI method suppresses close-resource warnings because ownership transfer is deliberate. If a user returns null or an invalid filter, native code may fail. The class-level SpotBugs exclusion in this subset includes this class, suggesting known static-analysis complexity around resource ownership.

## Test Signals
Tests should verify Java factory invocation, context flag propagation, name callback, native ownership transfer via `disOwnNativeHandle`, and disposal of the factory shared pointer after DB shutdown.
