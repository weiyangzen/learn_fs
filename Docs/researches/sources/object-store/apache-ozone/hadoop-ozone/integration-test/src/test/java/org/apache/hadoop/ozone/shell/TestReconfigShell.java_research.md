# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestReconfigShell.java

Purpose: This abstract non-HA integration test validates the `ozone admin reconfig` command against datanodes, OM, and SCM. It checks property listing, starting a reconfiguration task, runtime update of OM directory-deleting interval, and the bulk in-service datanode command.

Important APIs and types: It uses `OzoneAdmin`, `ReconfigurationHandler`, `ReconfigurableBase`, `OzoneManager`, `StorageContainerManager`, `HddsDatanodeService`, `DirectoryDeletingService`, `NodeManager`, `HddsProtos.NodeOperationalState`, `GenericTestUtils.PrintStreamCapturer`, and `LogCapturer`.

Control flow: `capture` initializes an admin shell, output capturers, and the OM reconfiguration handler from the shared non-HA cluster. Property tests execute `reconfig --service <service> --address <host:port> properties` and compare output with each service's `getReconfigurableProperties`. The interval test first sets the OM interval to `1m`, starts reconfig, waits for completion logs, and verifies the value from `ozone-site.xml` (`2m`) is applied and reported in status. Datanode tests execute the bulk `--in-service-datanodes` path and temporarily mark one datanode decommissioning to verify filtering.

State and persistence behavior: Runtime configuration state is mutated through `ReconfigurationHandler.reconfigureProperty` and reloaded from XML resources. The datanode out-of-service test mutates SCM node operational state and restores it. No permanent user data is created.

Dependencies and integration points: The class is nested under `NonHATests`, depends on the shared mini cluster, and integrates admin CLI parsing with service RPC endpoints, reconfigurable property registries, OM background service restart logic, SCM node manager state, and test resource `ozone-site.xml`.

Risks: Log-based waits can be timing-sensitive. Output capture resets only stdout explicitly in `stopCapture`, while stderr is captured but not closed there. The directory-deleting interval assertion depends on the test resource value remaining `2m`.

Test signals: Signals include empty stderr, output containing all reconfigurable properties, reconfiguration completion logs, `DirectoryDeletingService` restart log with 120 seconds, status output reporting finished and success for the interval key, and bulk datanode output containing the expected in-service count.
