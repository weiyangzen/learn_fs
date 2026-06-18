# sources/storage-engines/foundationdb/bindings/java/fdbJNI.cpp

## Purpose
`fdbJNI.cpp` is the native JNI bridge for the FoundationDB Java bindings. It exposes Java-native methods for FDB futures, database operations, transaction operations, options, network lifecycle, and JNI library load/unload hooks, translating between Java objects and FoundationDB C API handles.

## Important APIs, Types, and Functions
- Global JNI state includes `g_jvm`, thread-local `g_thread_jenv`, thread-local `g_IFutureCallback_call_methodID`, external-thread tracking, and cached global class/method references for range/key/mapped result objects.
- Error helpers include `throwOutOfMem`, `getThrowable`, `throwNamedException`, `throwRuntimeEx`, `throwParamNotNull`, and `safeThrow`.
- Future natives cover callback registration, blocking, error retrieval, readiness, cancellation, disposal, memory release, and typed getters for bool, int64, byte arrays, string arrays, key arrays, key-range arrays, range results, and mapped range results.
- Database natives create/destroy `FDBDatabase`, set database options, fetch main-thread busyness, create transactions, and return client status futures.
- Transaction natives cover read version, get, getKey, range scans, mapped range scans, direct-buffer result marshalling, estimated range size, split points, set, clear, clear range, atomic mutate, commit, options, committed version, approximate size, versionstamp, key locations, onError, dispose/reset/cancel/watch, and conflict ranges.
- Network/API natives cover API version selection, network options, setup, run, stop, and global reference initialization/cleanup in `JNI_OnLoad` and `JNI_OnUnload`.

## Control Flow
Java calls pass native pointer values as `jlong`. Each JNI method validates pointer and array parameters, converts Java strings or byte arrays into native buffers, calls the matching FDB C API, releases Java array elements with `JNI_ABORT` for input-only arrays, and returns either a native future pointer or a marshalled Java result. Future callbacks are registered by converting Java `Runnable` callbacks to global references and setting `fdb_future_set_callback`; callback execution attaches external client threads to the JVM as daemon threads when necessary, calls `Runnable.run`, then deletes the callback global reference.

Range result marshalling has two paths. Object-array paths copy native result bytes into Java `byte[]` and length arrays, then instantiate `RangeResult`, `KeyArrayResult`, `KeyRangeArrayResult`, `MappedRangeResult`, or `MappedKeyValue`. Direct-buffer paths write compact metadata and bytes into caller-provided direct buffers and truncate to the first result that fits while setting `more=true`.

`JNI_OnLoad` caches global references and constructor/static method IDs for frequently used Java result classes. `Network_run` records the network-thread `JNIEnv`, resolves callback method IDs, installs a network-thread completion hook to detach external threads, then calls `fdb_run_network`.

## State and Persistence Behavior
Native state is process-global: the selected API version, FDB network lifecycle, global class references, and thread-local JNI callback state. Database and transaction state lives in FDB C handles whose lifetime is controlled by explicit Java close/dispose calls. Futures hold native resources until destroyed, cancelled, or memory-released by Java wrappers. The bridge itself does not persist data, but transaction mutation methods directly mutate FoundationDB transaction state that is committed later.

## Dependencies and Integration Points
The file depends on generated JNI headers for Java binding classes, `foundationdb/fdb_c.h`, Java classes such as `FDBException`, `RangeResult`, `MappedRangeResult`, `MappedKeyValue`, `Range`, and `Runnable`, plus the FoundationDB C client library. It is the main integration point between Java APIs and the native C client ABI.

## Risks and Edge Cases
JNI error paths must be exact: missed releases can leak pinned arrays, and releasing with the wrong mode could copy unwanted input buffers back. Several methods allocate local references in loops without explicit cleanup, which can matter for very large result arrays. Callback registration deletes the Java global reference after one callback; this matches FDB future callback semantics but depends on callbacks never firing multiple times. External thread attach/detach relies on a network completion hook and thread-local flags; unusual callback threads or lifecycle races could leak attached daemon threads. Direct-buffer marshalling trusts the supplied `bufferCapacity` and writes native-endian `jint` values, so Java readers must match layout and byte order. `JNI_OnLoad` does not check every `FindClass`/`GetMethodID` result before creating global refs, so class signature drift can fail later or crash earlier depending on pending exceptions.

## Test Signals
Integration tests in this subset exercise many JNI paths: range and mapped range scans, futures and cancellation callbacks, watches, client status, transaction commit state, database opens, and external-client tags. Unit tests with disabled native calls check event counting around JNI calls but avoid real native execution. There is no focused stress test here for local reference limits, direct buffer overflow prevention beyond capacity truncation, or JNI class-cache failure handling.
