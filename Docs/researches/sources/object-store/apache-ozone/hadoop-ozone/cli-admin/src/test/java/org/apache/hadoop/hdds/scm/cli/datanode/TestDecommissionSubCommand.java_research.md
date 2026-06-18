<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestDecommissionSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestDecommissionSubCommand.java

Purpose: Tests datanode decommission command output and error handling when decommissioning hostnames from args or stdin.

Important APIs and types: `DecommissionSubCommand`, mocked `ScmClient.decommissionNodes`, `DatanodeAdminError`, Picocli, regex output checks, and captured stdout/stderr.

Control flow: Setup redirects streams and prepares the command. Tests feed hostnames through stdin using `-` or positional args, mock empty error results for success, or return per-host errors. The command is executed directly against the mock and output/error behavior is asserted.

State and persistence behavior: No real datanode state changes. Mocked SCM return values represent accepted decommission requests or validation errors.

Dependencies and integration points: Covers CLI parsing and output around SCM datanode admin decommission APIs.

Risks: Success output is accepted after SCM returns no errors, not after decommission completes. Error paths throw IOException after printing per-node errors.

Test signals: Stdin hostnames are all reported, successful decommission messages for host1/host2, error messages include node and cause, and IOException is thrown on reported errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestDecommissionSubCommand.java -->
