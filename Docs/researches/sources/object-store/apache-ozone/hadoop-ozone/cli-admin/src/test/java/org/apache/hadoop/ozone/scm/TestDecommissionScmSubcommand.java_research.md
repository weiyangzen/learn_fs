# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/ozone/scm/TestDecommissionScmSubcommand.java

Purpose: This test validates SCM decommission CLI input requirements, success reporting, and backend error propagation.

Important APIs and types: It uses `DecommissionScmSubcommand`, `OzoneAdmin`, mocked `ScmClient.decommissionScm`, `DecommissionScmResponseProto`, `GenericTestUtils` output capturers, and picocli.

Control flow: The first test invokes top-level `ozone admin scm decommission` without `--nodeid` and expects usage text on stderr, then parses a UUID node ID and stubs a successful response. The second stubs a failure response and expects an `IOException` containing the server error.

State and persistence behavior: No persistence is involved. Runtime state is a UUID option value and captured console output.

Dependencies and integration points: The suite anchors the admin command to SCM decommission RPC response semantics.

Risks: Usage validation is exercised through `OzoneAdmin.execute`, while execution success is tested directly on the subcommand, leaving some full CLI wiring untested.

Test signals: Usage output for missing node ID, success output containing the selected SCM ID, and thrown `IOException` when SCM reports `success=false`.
