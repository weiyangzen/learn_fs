<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/FinalizationStatusSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/FinalizationStatusSubCommand.java

Purpose: Implements OM upgrade finalization status querying. It asks the selected OM for current finalization progress without starting or taking over finalization and prints only the status enum.

Important APIs and types: `OzoneManagerProtocol.queryUpgradeFinalizationProgress`, `UpgradeFinalization.StatusAndMessages`, UUID-generated upgrade client IDs, and `OmAddressOptions.OptionalServiceIdOrHostMixin`.

Control flow: `call()` creates a unique `Upgrade-Client-<uuid>` ID, opens an OM client from service ID or host, invokes `queryUpgradeFinalizationProgress(upgradeClientID, false, true)`, prints `progress.status()`, and closes the client.

State and persistence behavior: No local persistence. It reads remote finalization state and does not request takeover. The random client ID avoids colliding with real finalization clients.

Dependencies and integration points: Used under `ozone admin om finalizationstatus`; shares address resolution with host-aware OM commands and relies on `UpgradeFinalization` protocol semantics.

Risks: Printing only the enum omits progress messages, so operators needing details must use finalize/monitor flows. Wrong host/service selection can report a different OM view.

Test signals: Verify the progress query flags, random client prefix shape, status output, host/service option parsing, and exception propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/FinalizationStatusSubCommand.java -->
