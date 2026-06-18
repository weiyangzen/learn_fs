# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestSafeModeCheckSubcommandHA.java

Purpose: This integration suite validates `ozone admin safemode status` against an HA cluster with three OMs and three SCMs. It verifies default leader selection, direct SCM targeting, all-node reporting, and verbose rule output.

Important APIs and types: It uses `MiniOzoneCluster.newHABuilder`, `MiniOzoneHAClusterImpl`, `StorageContainerManager`, `OzoneAdmin`, `OzoneConfiguration`, and `GenericTestUtils.PrintStreamCapturer`. Helper methods derive the SCM service ID and assert safe-mode rule names and SCM node output patterns.

Control flow: `init` builds an HA cluster with OM service `om-test`, SCM service `scm-test`, three OMs, and three SCMs, then waits for readiness. Each test captures stdout/stderr, copies the cluster configuration into the admin shell as overrides, executes a safemode status variant, and inspects text output. Variants cover no option, `--verbose`, `--scm <host:port>`, `--all`, and combinations with verbose.

State and persistence behavior: The suite does not mutate object-store state. Runtime state comes from SCM safe-mode status and the HA config entries used to map service/node IDs to client addresses. Captured output is closed after each test.

Dependencies and integration points: It integrates admin CLI parsing, SCM HA service discovery, leader lookup, SCM client addresses, and safe-mode rule reporting. It depends on configuration keys `ozone.scm.service.ids` and `ozone.scm.client.address.<service>.<node>`.

Risks: Text output assertions are format-sensitive, especially regexes around `[nodeId]: in/out of safe mode`. The rule list is hard-coded, so changes in safe-mode rule names require test updates. The class has no `@AfterAll` cluster shutdown, which may rely on test framework cleanup or process teardown.

Test signals: Signals include leader node ID in default output, service ID when targeting or listing all SCMs, every SCM node ID with an in/out safe-mode line, and verbose output containing DataNode, RatisContainer, HealthyPipeline, StateMachineReady, OneReplicaPipeline, and ECContainer safe-mode rules.
