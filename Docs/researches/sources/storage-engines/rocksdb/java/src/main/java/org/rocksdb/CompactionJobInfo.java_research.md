# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionJobInfo.java

Purpose: exposes native compaction-job metadata to Java callers and `EventListener` callbacks. APIs return column family name, status, thread/job identifiers, input and output levels, input/output file names, table properties, compaction reason, output compression, and optional `CompactionJobStats`.

Control flow is accessor-only JNI forwarding. The public constructor owns a new native struct; the private JNI constructor calls `disOwnNativeHandle()` because callback-created instances borrow C++ memory. `inputFiles()` and `outputFiles()` convert native arrays to fixed-size Java lists; `stats()` checks for native handle `0` before wrapping. State is native event/job state, usually ephemeral and tied to callback timing. Dependencies include `Status`, `TableProperties`, `CompactionReason`, `CompressionType`, and `CompactionJobStats`.

Risks: borrowed handle lifetime is critical, array/list results may be immutable-size views, unknown compaction reason/compression bytes can throw through enum conversion, and stats ownership differs from the parent info. Tests should exercise callback construction, null stats, table-property maps keyed by files, and disposal of owned versus disowned handles.
