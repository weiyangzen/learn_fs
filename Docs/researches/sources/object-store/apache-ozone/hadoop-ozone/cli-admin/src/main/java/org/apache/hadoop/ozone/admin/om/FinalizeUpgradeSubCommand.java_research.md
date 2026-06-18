<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/FinalizeUpgradeSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/FinalizeUpgradeSubCommand.java

Purpose: Starts and monitors OM metadata upgrade finalization. It handles already-finalized responses, invalid start responses, takeover of an existing monitor, and streaming finalization progress messages until completion.

Important APIs and types: `OzoneManagerProtocol.finalizeUpgrade`, `queryUpgradeFinalizationProgress`, `UpgradeFinalization` status helpers and emitters, `UpgradeException`, `ExecutorService`, `Future`, `CancellationException`, and `OmAddressOptions.OptionalServiceIdOrHostMixin`.

Control flow: `call()` creates an upgrade client ID, opens an OM client, and calls `finalizeUpgrade`. If the response is already finalized it prints and exits. If it is not a starting state, it reports an invalid response and throws. Otherwise `monitorAndWaitFinalization()` submits `UpgradeMonitor` to a single-thread executor. The monitor polls every 500 ms, prints ordered progress messages for in-progress or done states, exits on done, and handles the already-finalized takeover edge case.

State and persistence behavior: The command persists nothing locally. The server-side finalization changes OM metadata layout and enables finalized features. Runtime state is the generated client ID, `--takeover` flag, and monitor thread lifecycle.

Dependencies and integration points: Integrated under `OMAdmin`; shares status wording and error handling with `UpgradeFinalization` utility code. It depends on OM protocol finalization RPCs and host/service address selection.

Risks: The monitor loops indefinitely until the server reports done or an exception occurs. Interrupted monitoring emits cancellation but remote finalization may continue. `--takeover` changes ownership semantics for an in-flight request and must match server behavior.

Test signals: Mock responses for finalized, starting, invalid, in-progress, done, takeover, cancellation, interruption, and execution exception; assert emitted messages, executor shutdown, and `UpgradeException` handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/FinalizeUpgradeSubCommand.java -->
