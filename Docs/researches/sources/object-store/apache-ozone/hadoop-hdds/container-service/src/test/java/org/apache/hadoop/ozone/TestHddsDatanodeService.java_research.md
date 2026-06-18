## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/TestHddsDatanodeService.java

Purpose: this JUnit test class validates selected `HddsDatanodeService` startup, shutdown, JMX, and HTTP/HTTPS port behaviors.

Important APIs and tests: `setUp()` creates an `OzoneConfiguration` with SCM addresses, metadata and datanode volume dirs, a mock service plugin, security disabled, and token flags enabled. Tests include `testDeletedContainersClearedOnShutdown`, `testDatanodeUuidInMXBean`, and `testHttpPorts`. `MockService` is a no-op `ServicePlugin`.

Control flow and state: the deletion test starts the service under each key-value schema version, accesses the single `HddsVolume`, creates and moves a container into the deleted container directory, then stops, joins, closes, and shuts down metrics. It asserts deleted tmp containers are removed on shutdown. The JMX test reads `DatanodeUuid` from the platform MBean server and matches it to service details. The HTTP policy test checks published datanode HTTP/HTTPS ports according to `HttpConfig.Policy`.

Persistence and integration: tests create real temp metadata and volume directories, use `ContainerTestUtils` to create containers, and observe MBeans and metrics system behavior.

Risks and test signals: the setup intentionally validates that token misconfiguration does not block insecure datanode startup. Cleanup relies on explicit service close and `DefaultMetricsSystem.shutdown()` to prevent cross-test contamination. It is an integration-style test with real filesystem state.
