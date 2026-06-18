<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/compaction/log/CompactionFileInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/compaction/log/CompactionFileInfo.java

Purpose: Persistent compaction-log representation of an SST file, extending `SstFileInfo` with a mutable `pruned` flag.

Important APIs/types/functions: Constructors accept file name, optional start/end key range, column family, and prune status. `getProtobuf()` serializes to `HddsProtos.CompactionFileInfoProto`; `getFromProtobuf` deserializes. `Builder` requires non-null file name, can populate metadata from RocksDB `LiveFileMetaData`, and enforces all-or-none presence for start range, end range, and column family.

Control flow and state: `setPruned()` mutates the flag after construction. Serialization includes optional range fields only when present and always writes file name/pruned. Equality and hash code include base SST metadata and prune state.

Dependencies and integration points: Used by `CompactionLogEntry`, `CompactionDag.populateCompactionDAG`, and `RocksDBCheckpointDiffer` event listeners/pruning queue. The pruned bit records whether OMKeyInfo values have already been stripped from backed-up source SST files.

Risks: Mutability of `pruned` means objects shared from a log entry can change while referenced elsewhere. The all-or-none validation protects prefix filtering from partial metadata, but older legacy entries may intentionally lack all range fields.

Test signals: `TestCompactionFileInfo` covers valid/invalid builder combinations, pruned flag mutation, protobuf optional fields, and pruned deserialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/compaction/log/CompactionFileInfo.java -->
