## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/OnDemandScannerMetrics.java

Purpose: Metrics source for the on-demand container scanner.

Important APIs and functions: `create()` registers a source named `On-demand container scanner metrics` and inherits scanner counters from `AbstractContainerScannerMetrics`.

Control flow and state: No additional fields beyond the base metrics. Constructor is private to enforce Metrics2 registration through the factory.

Persistence and dependencies: In-memory Metrics2 telemetry only. Used by `OnDemandContainerScanner` and unregistered during scanner shutdown.

Risks: The fixed name can collide if multiple on-demand scanners are created in one metrics system without unregistering. It exposes no byte-rate metric even though on-demand scans use a throttler.

Test signals: Registration/unregistration, inherited scanned/unhealthy/iteration counters, duplicate creation behavior, and scanner shutdown cleanup.
