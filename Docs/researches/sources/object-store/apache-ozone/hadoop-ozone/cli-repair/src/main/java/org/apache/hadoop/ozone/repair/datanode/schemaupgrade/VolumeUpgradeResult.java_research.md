## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/schemaupgrade/VolumeUpgradeResult.java

Purpose: mutable result aggregate for one HDDS volume during datanode container schema upgrade. It records volume-level success/failure, elapsed time, the opened schema-three store, and per-container migration results.

Important APIs and control flow: the constructor pins an `HddsVolume`. `setResultList` converts a list of `ContainerUpgradeResult` values into a map keyed by original container ID. `success` and `fail` finalize elapsed time from `Time.monotonicNow`, set status, and preserve exceptions on failure. `toString` serializes volume root, every container result, summed row count, elapsed time, status, and exception details.

State and dependencies: no direct persistence; it mirrors migration state already written by the upgrade task. It references `DatanodeStoreSchemaThreeImpl`, so later verification can inspect migrated block data from the schema-three store.

Risks and test signals: `resultMap` can remain null when a volume fails early, so callers must check status. `TestUpgradeContainerSchema` asserts success, container status, backup/new container file paths, schema version transitions, and uses `getStore` to validate migrated rows.
