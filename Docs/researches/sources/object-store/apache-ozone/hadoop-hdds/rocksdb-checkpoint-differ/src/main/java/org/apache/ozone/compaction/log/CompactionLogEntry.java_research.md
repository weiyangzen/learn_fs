<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/compaction/log/CompactionLogEntry.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/compaction/log/CompactionLogEntry.java

Purpose: DAO and codec target for one RocksDB compaction event persisted in the compaction log table.

Important APIs/types/functions: Fields are DB sequence number, compaction time, input file info list, output file info list, and optional compaction reason. `CODEC` is a `DelegatedCodec` over `CompactionLogEntryProto`. Public APIs include getters, `getProtobuf`, `getFromProtobuf`, `toBuilder`, `equals`, `hashCode`, and `copyObject`. `Builder` constructs entries and can replace the input file list during value-pruning updates.

Control flow and state: The entry object stores list references as provided and is otherwise immutable. Serialization writes sequence/time, optional reason, and file-info protos. Deserialization rebuilds `CompactionFileInfo` lists before constructing the entry.

Dependencies and integration points: Written by `RocksDBCheckpointDiffer.addToCompactionLogTable`, loaded from RocksDB during DAG reconstruction, and updated after SST value pruning marks input files as pruned.

Risks: `copyObject` is shallow for lists and file info objects, so callers needing isolation must copy nested objects. Persisted key ordering is external to this class and must remain compatible with pruning scans.

Test signals: `TestCompactionLogEntry` covers protobuf round trip with and without compaction reason and equality of nested file info lists.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/compaction/log/CompactionLogEntry.java -->
