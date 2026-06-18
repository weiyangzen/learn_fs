## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerMetadataScannerMetrics.java

Purpose: Metrics source for the singleton background container metadata scanner.

Important APIs and functions: `create()` registers `ContainerMetadataScannerMetrics` with the default metrics system and inherits scanner counters from `AbstractContainerScannerMetrics`.

Control flow and state: The class adds no metrics beyond the base counters. Its constructor is private so callers use the registered factory.

Persistence and dependencies: In-memory Hadoop Metrics2 telemetry only. Depends on `DefaultMetricsSystem`.

Risks: The fixed source name means only one metadata scanner metrics instance should be registered at a time. Tests must unregister to avoid duplicate source conflicts.

Test signals: Create/register/unregister, inherited counter increments/resets, duplicate creation behavior, and metadata scanner lifecycle integration.
