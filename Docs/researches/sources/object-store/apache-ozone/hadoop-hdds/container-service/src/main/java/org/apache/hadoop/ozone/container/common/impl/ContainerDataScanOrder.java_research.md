<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerDataScanOrder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerDataScanOrder.java

Purpose: comparator for ordering containers for data scans.

Important APIs and control flow: `INSTANCE` exposes a reusable comparator. `compare` reads each container's `ContainerData.lastDataScanTime`, sorts unscanned containers before scanned containers, sorts scanned containers by oldest timestamp first, and breaks all ties by container ID.

State and persistence: no state beyond the singleton comparator. It consumes timestamps persisted through `ContainerData` but does not mutate them.

Dependencies and integration: used by `ContainerSet.getContainerIterator(HddsVolume)` to produce per-volume scan order. Depends on the `Container` interface and `ContainerData` scan timestamp API.

Risks and test signals: tests should cover both Optional-empty timestamps, one empty and one present, equal timestamps with ID tie-breaks, and stable behavior when containers are on the same volume. Since it reads mutable container data, concurrent timestamp updates can change ordering between list construction and scan execution.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerDataScanOrder.java -->
