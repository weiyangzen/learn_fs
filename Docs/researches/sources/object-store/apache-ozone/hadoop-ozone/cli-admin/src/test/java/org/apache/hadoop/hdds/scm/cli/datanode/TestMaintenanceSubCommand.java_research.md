# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestMaintenanceSubCommand.java

Purpose: This suite validates the datanode maintenance CLI behavior when hostnames come from arguments or stdin and when SCM reports per-host administration errors.

Important APIs and types: It uses `MaintenanceSubCommand`, mocked `ScmClient`, `DatanodeAdminError`, picocli `CommandLine`, and captured `System.out`/`System.err`.

Control flow: Setup redirects console streams and creates a mock client. Tests parse either `"-"` for stdin or explicit hostnames, then call `cmd.execute(scmClient)`. Success paths expect a heading and listed hosts; the failure path stubs `startMaintenanceNodes` to return one `DatanodeAdminError` and expects `IOException`.

State and persistence behavior: No durable state is written. Input state may be `System.in`, and output state is captured byte buffers.

Dependencies and integration points: The command is integrated with `ScmClient.startMaintenanceNodes(List, int, boolean)`, stdin hostname parsing, and CLI user-facing error reporting.

Risks: The stdin test stubs `decommissionNodes` even though normal maintenance uses `startMaintenanceNodes`, so that path may not fully assert the current backend call. Exact regex output checks can be brittle to text revisions.

Test signals: Expected maintenance heading, host echoing, stderr line `Error: host1: host1 error`, and thrown `IOException` when SCM returns errors.
