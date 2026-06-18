<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/CompactionNode.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/CompactionNode.java

Purpose: Graph node representing one SST file in the compaction DAG, extending SST metadata with snapshot generation and traversal counters.

Important APIs/types/functions: Constructors accept raw fields or `CompactionFileInfo`. Public methods expose `snapshotGeneration`, `totalNumberOfKeys`, `cumulativeKeysReverseTraversal`, and mutators for cumulative reverse traversal. `equals` is final and identity-only; `hashCode` hashes file name.

Control flow and state: The main constructor stores inherited file metadata and initializes total/cumulative key counts to zero. `snapshotGeneration` is immutable. Cumulative traversal state is mutable but not used heavily in the current differ path.

Dependencies and integration points: Created by `CompactionDag`; returned as `SstFileInfo`-compatible diff entries in `RocksDBCheckpointDiffer.internalGetSSTDiffList` when traversal reaches different files.

Risks: Identity equality with filename hash code violates the usual equals/hashCode expectation for separately constructed nodes with the same file name. The DAG relies on canonical nodes in `compactionNodeMap` to avoid duplicate logical nodes.

Test signals: DAG pruning and diff traversal tests exercise node identity through graph membership and file-name extraction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/CompactionNode.java -->
