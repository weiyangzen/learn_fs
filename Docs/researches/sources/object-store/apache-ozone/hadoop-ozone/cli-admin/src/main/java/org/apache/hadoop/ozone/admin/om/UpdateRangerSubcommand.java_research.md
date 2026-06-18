<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/UpdateRangerSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/UpdateRangerSubcommand.java

Purpose: Triggers the OM leader's Ranger background sync task to push policy and role updates to Ranger, optionally without waiting for completion.

Important APIs and types: `OzoneManagerProtocol.triggerRangerBGSync(boolean)`, `OmAddressOptions.OptionalServiceIdOrHostMixin`, `--no-wait`, and Picocli command metadata.

Control flow: The command opens an OM client, invokes `triggerRangerBGSync(noWait)`, prints success on true, and prints an error message to stderr on false. RPC exceptions propagate.

State and persistence behavior: No local state. Remote side may enqueue or run Ranger sync work and update Ranger-side policies/roles depending on OM implementation and authorization.

Dependencies and integration points: Depends on OM admin privilege, Ranger integration, and host/service OM address resolution.

Risks: A false result produces stderr but no exception, so exit-code behavior may still be success. With `--no-wait`, the command can return before the background task result is known.

Test signals: Mock true/false returns, verify stdout/stderr split, no-wait flag propagation, and RPC failure handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/UpdateRangerSubcommand.java -->
