<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/snapshot/DefragSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/snapshot/DefragSubCommand.java

Purpose: Triggers the OM snapshot defragmentation service on a selected OM node, with optional asynchronous no-wait behavior.

Important APIs and types: `AbstractSubcommand`, `OmAddressOptions.OptionalServiceIdMixin`, `OMNodeDetails.getOMNodeDetailsFromConf`, `OMAdminProtocolClientSideImpl.createProxyForSingleOM`, `UserGroupInformation`, `triggerSnapshotDefrag(boolean)`, `--node-id`, and `--no-wait`.

Control flow: `call()` resolves OM node details from configuration, service ID, and optional node ID. If resolution fails it prints an error and returns. Otherwise it creates a single-OM admin proxy and calls `execute`. `execute` prints a trigger message, invokes `triggerSnapshotDefrag(noWait)`, and prints background-triggered, completed, or failed/interrupted messaging based on `noWait` and the boolean result.

State and persistence behavior: No local persistence. Remote OM snapshot DB/files may be compacted or defragmented by the service. The command's boolean result is the only observed completion state.

Dependencies and integration points: Registered below `SnapshotSubCommand`; requires HA OM configuration and single-OM admin protocol access.

Risks: If `--node-id` is omitted in multi-OM configs, resolution semantics are delegated to `OMNodeDetails`. A false result only prints failure text and does not throw. `--no-wait` reports successful trigger without knowing final service outcome.

Test signals: Mock node-detail resolution, client creation, true/false/no-wait outcomes, IOException propagation and stderr message, and HA config failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/snapshot/DefragSubCommand.java -->
