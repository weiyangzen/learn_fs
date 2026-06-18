<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/TablePrefixInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/TablePrefixInfo.java

Purpose: Immutable holder for table/column-family prefix strings used to filter SST files during snapshot diff.

Important APIs/types/functions: Constructor wraps the provided `Map<String,String>` with `Collections.unmodifiableMap`. Public methods are `getTablePrefix(String)`, `size()`, `getTableNames()`, and `toString()`.

Control flow and state: There is no mutation after construction. Missing table names return the empty string, allowing callers to treat absent prefixes as broad/no-prefix lookups.

Dependencies and integration points: Used by `RocksDiffUtils.filterRelevantSstFiles` and `RocksDBCheckpointDiffer.getSSTDiffList` to remove SST files whose key range cannot contain requested table prefixes.

Risks: The constructor does not make a defensive copy, so later mutation of the original map can affect the unmodifiable view. Empty prefix fallback can make filters permissive if table names are missing.

Test signals: Filter behavior is indirectly testable through RocksDiffUtils and snapshot diff tests with table-specific key ranges.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/TablePrefixInfo.java -->
