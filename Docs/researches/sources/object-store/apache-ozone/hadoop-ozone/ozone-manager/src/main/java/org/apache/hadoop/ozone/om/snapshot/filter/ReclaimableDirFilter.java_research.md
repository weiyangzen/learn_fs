## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/filter/ReclaimableDirFilter.java

Purpose: reclaim filter for deleted directory markers, deciding whether a directory can be removed because it is not referenced by the previous snapshot.

Important APIs and types: extends `ReclaimableFilter<OmKeyInfo>` with one previous snapshot. Overrides volume/bucket extraction and `isReclaimable`.

Control flow: for each deleted directory entry, gets the previous snapshot's `KeyManager` if available and calls `getPreviousSnapshotOzoneDirInfo`. A directory is reclaimable when no previous snapshot exists, the previous directory is absent, or its object ID differs.

State and persistence: no own durable state; uses base class snapshot locks and cached previous snapshot handles.

Dependencies and integration: used by snapshot GC/purge logic over deleted directory entries, and depends on FSO directory lookup semantics in `KeyManager`.

Risks and test signals: object-ID equality is the only preservation signal; ACL-only directory changes are not relevant to reclaim. Tests should cover no previous snapshot, matching object ID retained, different object ID reclaimable, deleted volume/bucket handling inherited from base filter, and lock reacquisition on chain changes.
