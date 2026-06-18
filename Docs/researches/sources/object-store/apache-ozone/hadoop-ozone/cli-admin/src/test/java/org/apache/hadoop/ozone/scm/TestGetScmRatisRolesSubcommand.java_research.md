# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/ozone/scm/TestGetScmRatisRolesSubcommand.java

Purpose: This unit test verifies table-formatted output for the SCM HA Ratis roles command.

Important APIs and types: It uses `GetScmRatisRolesSubcommand`, mocked `ScmClient.getScmRoles`, picocli, and `GenericTestUtils.SystemOutCapturer`.

Control flow: The test parses `--table`, stubs three colon-separated SCM role strings, executes the command, and checks formatted rows for hostname, port, role, and UUID alignment.

State and persistence behavior: There is no persistent state. The input state is a list of role strings returned by SCM.

Dependencies and integration points: The command depends on SCM role strings using `host:port:role:id:ip` layout and transforms them into operator-readable table output.

Risks: The parser contract for role strings is implicit; malformed entries are not covered. Assertions depend on spacing in the table formatter.

Test signals: Captured output contains all three formatted role rows, including LEADER and FOLLOWER alignment.
