# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionOptionsFIFO.java

Purpose: native option wrapper for FIFO compaction policy. APIs configure table-file size trimming, intra-L0 compaction allowance, combined SST/blob data-file size limit, and key-value-ratio compaction.

Control flow is simple JNI setter/getter forwarding after construction through `newCompactionOptionsFIFO()`. State lives in the native options object and is later embedded in column-family compaction options, affecting file deletion and compacting behavior under FIFO style. Integration points include `ColumnFamilyOptions`, FIFO compaction style selection, blob-file aware size accounting, and L0 file compaction thresholds described in comments.

Risks: defaults and triggering logic are enforced in C++ and can drift from Java comments, `maxDataFilesSize` changes FIFO accounting from SST-only to SST+blob, and enabling compaction can unexpectedly increase write amplification. Tests should verify Java/native round-trips, default values, behavior when blob files exist, and lifecycle disposal. The JNI signatures are the main contract to keep in sync with native RocksDB options.
