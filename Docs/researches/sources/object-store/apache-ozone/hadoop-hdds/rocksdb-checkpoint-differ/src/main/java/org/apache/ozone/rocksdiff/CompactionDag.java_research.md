<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/CompactionDag.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/CompactionDag.java

Purpose: In-memory representation of SST compaction history as paired directed graphs plus a file-name-to-node map.

Important APIs/types/functions: `populateCompactionDAG` creates/reuses `CompactionNode`s for input/output `CompactionFileInfo` values and draws edges. `forwardCompactionDAG` stores edges from output SST to input SST. `backwardCompactionDAG` stores edges from input SST to output SST. `pruneNodesFromDag`, `pruneBackwardDag`, and `pruneForwardDag` remove connected history around old snapshot levels. Accessors expose both graphs, the map, and node lookup.

Control flow and state: Nodes are inserted with `computeIfAbsent`; output files are outer-looped, input files inner-looped, and self-edges are skipped. Pruning walks level by level through predecessors or successors, removing nodes and collecting file names. `pruneNodesFromDag` prunes both graph directions and removes start nodes from the node map.

Dependencies and integration points: Used by `RocksDBCheckpointDiffer` to populate history from live compaction events and persisted compaction log entries, traverse diffs, and prune old history.

Risks: Guava `MutableGraph` is not inherently thread-safe; callers synchronize in `RocksDBCheckpointDiffer` during mutation/traversal-sensitive operations. `CompactionNode.equals` is identity-based while hash code uses file name, so node reuse through the map is important.

Test signals: `TestCompactionDag` validates forward/backward prune scenarios and end-to-end pruning after log/table reconstruction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/CompactionDag.java -->
