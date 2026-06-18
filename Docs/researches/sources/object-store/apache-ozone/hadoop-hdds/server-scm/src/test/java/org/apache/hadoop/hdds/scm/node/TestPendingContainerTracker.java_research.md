# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestPendingContainerTracker.java

Purpose: verifies `PendingContainerTracker` and per-datanode pending allocation buckets used to reserve space for containers that have been allocated but not yet confirmed by reports.

Important APIs and types: setup creates a tracker with 5 GiB max container size, 1000 `DatanodeInfo` instances with large default storage reports, and 10,000 `ContainerID`s. Tests call `checkSpaceAndRecordAllocation()`, `removePendingAllocation()`, and inspect `DatanodeInfo.getPendingContainerAllocations()` count/contains behavior. Storage reports are generated with `HddsTestUtils.createStorageReports()`.

Control flow: tests cover recording one allocation per datanode, removals, two-window rolling expiration after two intervals, removing nonexistent containers, unknown datanode zero count, multi-threaded add/remove operations, retaining empty buckets for reuse, removal from current/previous windows, many containers on one datanode, many datanodes with multiple containers, idempotent repeated recording, and multi-volume space checks where aggregate remaining is insufficient, pending slots consume per-volume capacity, and committed bytes reduce available slots.

State and persistence: all state is in-memory in datanode pending allocation windows and storage report snapshots. The rolling-window test uses real sleeps with a short interval; concurrency test uses Java threads.

Integration points and risks: protects placement/space accounting from over-allocating containers before reports catch up. Risks include timing sensitivity in roll-window tests, absence of explicit assertions after the concurrency test beyond no exceptions, and synthetic storage reports that may not cover all production volume edge cases.
