<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/RocksDiffUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/RocksDiffUtils.java

Purpose: Static helper methods for filtering SST diff candidates by table/column-family prefix coverage.

Important APIs/types/functions: `isKeyWithPrefixPresent(prefix, firstDbKey, lastDbKey)` checks whether a prefix falls within an SST key range using first-N-character comparisons. `filterRelevantSstFiles` overloads mutate a map or set of `SstFileInfo` by removing nodes for which `shouldSkipNode` returns true. `shouldSkipNode` is test-visible and handles missing metadata, empty prefix info, column-family mismatch, and key-range prefix exclusion.

Control flow and state: The filters iterate with mutable iterators and remove irrelevant entries in place. Missing start/end/column-family metadata returns false for backward compatibility, keeping the file rather than risking false exclusion.

Dependencies and integration points: Called by `RocksDBCheckpointDiffer.getSSTDiffList` after DAG/full diff candidate computation. Depends on `TablePrefixInfo` and `SstFileInfo`.

Risks: String-prefix comparison assumes keys are ordered compatibly with Java string comparison and table prefixes map exactly to encoded RocksDB keys. Missing metadata makes filtering conservative, increasing diff work.

Test signals: Useful tests include prefix within/outside range, missing metadata, empty prefix info, column-family exclusion, and map/set mutation behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/RocksDiffUtils.java -->
