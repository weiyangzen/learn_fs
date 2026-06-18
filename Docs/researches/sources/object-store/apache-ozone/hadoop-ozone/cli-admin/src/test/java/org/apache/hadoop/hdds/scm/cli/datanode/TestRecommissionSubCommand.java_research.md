# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestRecommissionSubCommand.java

Purpose: This test file verifies recommission CLI output and error propagation for datanode host lists passed directly or read from stdin.

Important APIs and types: It uses `RecommissionSubCommand`, mocked `ScmClient.recommissionNodes`, `DatanodeAdminError`, picocli, byte-array console capture, and regex-based assertions.

Control flow: Tests parse stdin marker `"-"` or host arguments, invoke the command, then assert that the command prints a recommission heading and each hostname. The error test returns a single admin error, expects `IOException`, and checks stderr for the formatted error.

State and persistence behavior: There is no on-disk state. Temporary state is limited to `System.in`, redirected `System.out`/`System.err`, and Mockito stubs.

Dependencies and integration points: The suite anchors the CLI user contract around `ScmClient.recommissionNodes(List)` and host ingestion from both terminal input styles.

Risks: Like the maintenance test, the stdin test stubs `decommissionNodes` instead of the recommission method, so it mostly verifies output parsing and not the backend invocation in that path.

Test signals: Recommission heading, exact host lines, stderr admin error formatting, and `IOException` on non-empty SCM error results.
