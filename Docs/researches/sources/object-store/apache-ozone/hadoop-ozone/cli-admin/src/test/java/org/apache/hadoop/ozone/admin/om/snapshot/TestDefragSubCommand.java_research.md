# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/ozone/admin/om/snapshot/TestDefragSubCommand.java

Purpose: This suite verifies OM snapshot defragmentation CLI behavior for wait/no-wait execution and service/node targeting options.

Important APIs and types: It defines `TestableDefragSubCommand` to override `createClient`, uses mocked `OMAdminProtocolClientSideImpl`, `OzoneConfiguration`, `OMNodeDetails`, Mockito verification, and picocli.

Control flow: Setup injects the mock client and redirects output. Tests parse default or option-rich arguments, execute the command, verify `triggerSnapshotDefrag` is called with `false` for waiting or `true` for no-wait, and assert success/failure text.

State and persistence behavior: No persistent state is changed. The command would normally open an OM admin protocol client; the test replaces it with a mock and verifies close behavior is harmless.

Dependencies and integration points: It anchors the admin CLI contract to OM admin RPC for snapshot defrag service control.

Risks: The test calls `cmd.execute(omAdminClient)` directly despite the override being available, so connection construction and service-id/node-id resolution are not deeply exercised.

Test signals: Correct boolean passed to `triggerSnapshotDefrag`, success text, failure/interruption text, and background execution message under `--no-wait`.
