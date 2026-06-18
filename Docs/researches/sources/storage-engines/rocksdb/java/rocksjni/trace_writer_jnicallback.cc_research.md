<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/trace_writer_jnicallback.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/trace_writer_jnicallback.cc

Purpose: Implements a C++ `TraceWriter` that delegates trace writes, close, and file-size queries to a Java `AbstractTraceWriter`.

Important APIs/types/functions: Constructor resolves Java proxy method IDs for write, close, and get-file-size. `Write(const Slice&)` calls Java `writeProxy(long-like Slice pointer)`, unpacks a short status code/subcode into C++ `Status`. `Close()` does the same for close. `GetFileSize()` calls the Java file-size method and returns a `uint64_t`.

Control flow: RocksDB tracing calls the C++ virtual methods. Each method obtains/attaches a `JNIEnv`, invokes the cached Java method, handles pending exceptions by describing them and returning an IO error or zero, converts Java status encoding through `StatusJni::toCppStatus`, and releases the JNI environment.

State and persistence behavior: The callback holds method IDs and a Java callback reference through `JniCallback`. Trace bytes are persisted or buffered by Java-side writer behavior, not by this C++ file.

Dependencies and integration points: Depends on `trace_writer_jnicallback.h` and `portal.h` for `StatusJni`, callback environment handling, and `Slice` exposure. Created by `trace_writer.cc` and consumed by `RocksDB.startTrace`.

Risks: `Write` passes `&data` directly to Java as an argument matching the generated proxy signature; Java must treat it as a temporary native slice valid only during the call. Exceptions are printed to stderr and converted to generic IO errors, losing Java exception detail. Method lookup failure leaves cached IDs null. Status packing into `jshort` must remain synchronized with Java.

Test signals: Tests should make Java write return OK and non-OK statuses, throw exceptions, verify close status conversion, assert file size conversion, and ensure Java does not retain the temporary slice pointer.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/trace_writer_jnicallback.cc -->
