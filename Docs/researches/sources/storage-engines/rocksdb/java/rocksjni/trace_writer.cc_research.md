<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/trace_writer.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/trace_writer.cc

Purpose: Constructs native `TraceWriterJniCallback` objects for Java `AbstractTraceWriter` implementations.

Important APIs/types/functions: `Java_org_rocksdb_AbstractTraceWriter_createNewTraceWriter` allocates `ROCKSDB_NAMESPACE::TraceWriterJniCallback(env, jobj)` and returns the native pointer.

Control flow: Java creates a trace writer object, calls this native constructor, and later passes the handle to `RocksDB.startTrace`, where ownership is transferred to RocksDB.

State and persistence behavior: The callback object is in-memory state. Actual trace persistence depends on the Java writer implementation invoked by `trace_writer_jnicallback.cc`.

Dependencies and integration points: Includes generated `org_rocksdb_AbstractTraceWriter.h`, pointer conversion helpers, and `trace_writer_jnicallback.h`. Integrates with `rocksjni.cc` `startTrace`.

Risks: The file comment mentions `CompactionFilterFactory`, but the implementation is trace writer creation. Ownership changes after `startTrace`; Java must not double-dispose. Constructor method-ID lookup failures need Java-side exception handling.

Test signals: Tests should create a Java trace writer, start/end tracing, verify write/close/file-size callbacks, and confirm ownership/disposal behavior after start.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/trace_writer.cc -->
