## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/CompositeDeltaDiffComputer.java

Purpose: orchestrates delta SST selection between snapshots, preferring checkpoint-differ DAG results and falling back to full SST comparison.

Important APIs and types: public constructor wires `RDBDifferComputer` when full diff is not forced, always wires `FullDiffComputer`, and accepts an activity reporter. Overrides `computeDeltaFiles` and `close`.

Control flow: attempts `RDBDifferComputer` with substatus `SST_FILE_DELTA_DAG_WALK`; on exception or empty result logs a warning and executes `FullDiffComputer` with substatus `SST_FILE_DELTA_FULL_DIFF`. If non-native diff mode is enabled, it also adds all relevant SSTs from the from-snapshot so delete/tombstone information is available to higher layers.

State and persistence: creates temporary hard links under child directories of the supplied delta directory and removes them on close through child computers and the superclass.

Dependencies and integration: used by `SnapshotDiffManager` and `SnapshotDefragService`. Depends on `OmSnapshotManager`, active metadata table prefixes, `SstFileInfo`, and raw/non-native SST read behavior.

Risks and test signals: fallback can be expensive and should preserve correctness. Non-native mode can enlarge delta input substantially. Tests should verify activity transitions, forced-full disabling of RDB differ, fallback on RDB differ exception, non-native addition of from-snapshot files, duplicate path handling in the returned map, and recursive cleanup on close.
