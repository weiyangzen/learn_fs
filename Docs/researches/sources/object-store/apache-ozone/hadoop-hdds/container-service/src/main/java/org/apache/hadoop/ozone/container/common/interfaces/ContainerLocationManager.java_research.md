<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerLocationManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerLocationManager.java

Purpose: abstraction for choosing physical paths for container placement and reporting storage locations.

Important APIs and control flow: `getContainerPath` returns a base path for a new container and metadata, `getDataPath` returns a data path for a specific container name, `getLocationReport` returns storage usage reports, and `shutdown` performs clean resource release.

State and persistence: interface only. Implementations likely hold volume lists, selection policy state, and sampled usage data.

Dependencies and integration: used by container creation and node reporting. Report type is `StorageLocationReport`.

Risks and test signals: tests should cover no available volumes, failed volumes, path creation errors, deterministic data path derivation, report freshness, and clean shutdown under exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerLocationManager.java -->
