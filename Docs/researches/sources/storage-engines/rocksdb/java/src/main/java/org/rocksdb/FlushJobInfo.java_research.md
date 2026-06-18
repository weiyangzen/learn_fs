# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/FlushJobInfo.java

Purpose: immutable Java payload for flush completion/start events. It captures column family ID/name, output file path, thread/job ID, write slowdown/stop flags, sequence-number range, table properties, and flush reason.

Control flow is package-private construction from JNI/tests; constructor converts the native flush-reason byte using `FlushReason.fromValue`. Public getters expose fields, and value-object methods compare all fields. State is copied Java callback data, not native-owned state, except nested objects must be valid Java wrappers. Dependencies include `TableProperties`, `FlushReason`, `Objects`, and `EventListener`.

Risks: unknown flush-reason bytes throw during construction, table-properties equality affects value semantics, and slowdown/stop flags are point-in-time signals. Tests should cover construction for all flush reasons, equality/hash/toString, listener payload correctness, and behavior when RocksDB enters L0 write slowdown/stop conditions.
