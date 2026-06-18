# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestScmAdminHA.java

Purpose: This small abstract HA test verifies that the SCM admin roles command can execute against an SCM endpoint in a shared HA cluster. It is a command-smoke test for `ozone admin --scm <host:port> scm roles`.

Important APIs and types: It uses `OzoneAdmin`, `MiniOzoneCluster`, `StorageContainerManager.getClientRpcAddress`, and the `HATests.TestCase` interface for cluster injection.

Control flow: `init` creates the admin shell and stores the cluster reference from the enclosing HA test harness. `testGetRatisRoles` builds `host:port` from the current storage container manager client RPC address and executes the `scm roles` command with `--scm`.

State and persistence behavior: The test does not create or mutate persistent data. It only reads SCM HA/Ratis role state through the admin command path.

Dependencies and integration points: It is nested in `HATests`, so it shares a three-OM/three-SCM HA cluster. The integration point is admin CLI dispatch to SCM role-reporting RPCs over a specific SCM client endpoint.

Risks: There are no assertions on stdout or role content, so this test only catches command execution failures and uncaught exceptions. If role output regresses semantically but command exit remains successful, this file will not catch it.

Test signals: The sole signal is successful command execution without throwing from `ozoneAdmin.execute`.
