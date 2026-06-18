# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/NativePointerHolder.java

## Purpose
Base class for Java wrappers that carry native SQLite pointer values across JNI while preserving some Java type separation.

## Important APIs, Types, And Functions
Generic `NativePointerHolder<ContextType>` contains private volatile `long nativePointer`, package-private `clearNativePointer()`, and public `getNativePointer()`.

## Control Flow
JNI sets the private field directly. Public wrappers pass `getNativePointer()` to native methods. Close/finalize-style CApi wrappers call `clearNativePointer()` to transfer the old pointer to native cleanup and zero the Java handle.

## State And Persistence Behavior
The only state is the volatile pointer value. The object does not own native memory by itself; ownership is controlled by the SQLite API and explicit close/finalize/free methods.

## Dependencies And Integration Points
Subclassed by opaque handle wrappers such as `sqlite3`, `sqlite3_stmt`, `sqlite3_blob`, `sqlite3_backup`, `sqlite3_context`, and `sqlite3_value`.

## Risks And Edge Cases
Using a handle after `clearNativePointer()` produces a zero pointer. The class does not prevent double-close races or operations on stale handles beyond clearing local state. Volatile gives visibility but not full lifecycle synchronization.

## Test Signals
Open/finalize/close tests should verify pointer clearing, double close behavior, and misuse handling for stale wrappers.
