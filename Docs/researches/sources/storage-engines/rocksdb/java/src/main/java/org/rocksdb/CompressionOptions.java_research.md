# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompressionOptions.java

Purpose: native wrapper for compression tuning. APIs set/get window bits, compression level, strategy, maximum dictionary bytes, zstd training bytes, and an `enabled` flag for bottommost compression options.

Control flow is one-to-one JNI forwarding after allocating `newCompressionOptions()`. State lives in the native object and is used by column-family compression settings and bottommost compression settings; Java does not validate codec-specific ranges. Dependencies include `RocksObject`, compression libraries through native RocksDB, and column-family option consumers.

Risks: invalid codec parameters are accepted at Java level and may fail or degrade behavior natively; comments describe bottommost-option semantics that can be subtle because `enabled=false` means different things depending on which option slot consumes it. Tests should round-trip every property, cover zstd dictionary training settings, verify bottommost compression behavior, and assert disposal frees the native handle.
