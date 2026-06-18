# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/PendingContainerTracker.java

Purpose: `PendingContainerTracker` prevents SCM from over-allocating containers to a datanode before that datanode reports the new containers in heartbeat reports. It records pending allocations per datanode using a two-window tumbling bucket.

Important APIs and types: Public APIs are `checkSpaceAndRecordAllocation`, `removePendingAllocation`, and visible `getMetrics`. The nested `TwoWindowBucket` exposes synchronized rolling, containment, removal, count, and `checkSpaceAndAdd` logic. It uses `DatanodeInfo`, `ContainerID`, `StorageReportProto`, `VolumeUsage.getUsableSpace`, and `SCMNodeMetrics`.

Control flow: Each datanode owns a `TwoWindowBucket`. Calling `checkSpaceAndRecordAllocation` validates inputs, rejects missing storage reports, rolls the bucket through `DatanodeInfo.getPendingContainerAllocations`, and atomically checks whether usable disk-space-derived container slots exceed current pending count. If so it adds the container to the current window and increments added metrics; otherwise it increments skipped-full-node metrics. Confirmed containers are removed from both windows.

State and persistence behavior: Pending allocation state is in-memory and ages automatically. A single roll moves current allocations to previous and clears current; two elapsed intervals drop both windows. State is not persisted across SCM restart, which is acceptable because datanode reports reestablish actual container state.

Dependencies and integration points: `NodeManager.checkSpaceAndRecordAllocation` and placement/container allocation paths use this tracker. Metrics are shared with SCM node metrics. `DatanodeInfo` owns the per-node bucket so allocation and report state live together.

Risks: Capacity is approximated as usable space divided by max container size; it does not model partial reservations or per-volume placement constraints beyond usable bytes. If reports are stale or empty, allocation is rejected. The two-window aging window trades correctness for eventual cleanup; unreported allocations can disappear after two intervals and allow new allocations.

Test signals: Tests should cover empty reports returning false, add/remove metric increments, per-volume usable-space aggregation, duplicate container additions, single and double roll behavior, removal from both windows, and concurrent check-and-add atomicity.
