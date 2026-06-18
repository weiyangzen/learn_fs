## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/filter/ReclaimableKeyFilter.java

Purpose: reclaim filter for deleted key entries and calculator for previous snapshot exclusive size.

Important APIs and types: extends `ReclaimableFilter<OmKeyInfo>` with two previous snapshots. Public accessors expose `exclusiveSizeMap` and `exclusiveReplicatedSizeMap`.

Control flow: for a deleted key, it memoizes lookup in the immediately previous snapshot using `KeyManager.getPreviousSnapshotOzoneKeyInfo`; if absent, the deleted key is reclaimable. If present, it checks the previous-to-previous snapshot to see whether the key is exclusive to the previous snapshot and updates exclusive size counters, then returns false because a previous snapshot still references the key.

State and persistence: keeps in-memory maps from snapshot UUID to exclusive logical and replicated sizes. Reclaim decisions read prior snapshot key/file tables but do not write metadata directly.

Dependencies and integration: used by snapshot GC over deleted key tables and by snapshot accounting logic that consumes exclusive size maps. Uses `SnapshotUtils.isBlockLocationInfoSame` plus object-ID equality to decide whether prior key info represents the same block data.

Risks and test signals: hsync special handling comes from `SnapshotUtils`; non-hsync keys with same object ID but different block locations are considered not present. Exclusive size updates happen as side effects even though the entry is not reclaimable. Tests should cover absent previous key, present previous key, absent previous-to-previous key exclusive accounting, replicated size aggregation, object-ID mismatch, block-location mismatch, memoization behavior, and OBS/FSO bucket layout lookup through `KeyManager`.
