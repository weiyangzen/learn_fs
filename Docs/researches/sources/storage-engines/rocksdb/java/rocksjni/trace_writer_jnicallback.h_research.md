<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/trace_writer_jnicallback.h -->
# sources/storage-engines/rocksdb/java/rocksjni/trace_writer_jnicallback.h

Purpose: Declares the JNI-backed C++ `TraceWriter` implementation.

Important APIs/types/functions: `class TraceWriterJniCallback : public JniCallback, public TraceWriter` declares constructor and overrides `Status Write(const Slice&)`, `Status Close()`, and `uint64_t GetFileSize()`. It stores method IDs for write, close, and file size.

Control flow: RocksDB sees this object through the `TraceWriter` interface, while Java disposal/ownership uses `JniCallback` behavior.

State and persistence behavior: Declares process-local callback state. Persistent trace output is delegated to Java-side methods.

Dependencies and integration points: Includes JNI, `rocksdb/trace_reader_writer.h`, and `rocksjni/jnicallback.h`. Implemented in `trace_writer_jnicallback.cc`.

Risks: Multiple inheritance requires both base classes to have compatible virtual destruction. The callback must outlive RocksDB trace usage and is owned by `StartTrace` after transfer.

Test signals: Compile tests catch virtual signature drift. Runtime tests should cover ownership transfer, virtual dispatch through `TraceWriter`, and destruction through callback/base paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/trace_writer_jnicallback.h -->
