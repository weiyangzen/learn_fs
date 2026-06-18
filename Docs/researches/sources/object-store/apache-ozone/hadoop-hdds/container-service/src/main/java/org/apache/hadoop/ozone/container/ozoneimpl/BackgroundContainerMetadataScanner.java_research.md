## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/BackgroundContainerMetadataScanner.java

Purpose: Single background scanner that verifies metadata for all loaded containers across volumes.

Important APIs and functions: The constructor sets the metadata scan interval, controller, metrics, and scan helper. `getContainerIterator()` iterates all containers through `ContainerController`. `scanContainer()` delegates to `scanHelper.scanMetadata()`. `getMetrics()` returns metadata scanner metrics.

Control flow and state: Inherits thread lifecycle, pause, and sleep behavior from `AbstractBackgroundContainerScanner`. Unlike data scanning, there is one scanner for all volumes.

Persistence and dependencies: Metadata scans can mark containers unhealthy and trigger volume failure scans but do not update data scan timestamps. Depends on `ContainerController`, `ContainerScanHelper`, and `ContainerMetadataScannerMetrics`.

Risks: A slow or stuck metadata scan blocks scanning for all volumes. The same min scan gap used by the helper can skip recently data-scanned containers. Exceptions per container are caught by the base scanner, but unchecked helper failures can exit the thread.

Test signals: Iterate all containers, skip failed-volume/recently-scanned containers, mark unhealthy metadata errors, transient too-many-open-files handling, metrics increment/reset, and scanner lifecycle.
