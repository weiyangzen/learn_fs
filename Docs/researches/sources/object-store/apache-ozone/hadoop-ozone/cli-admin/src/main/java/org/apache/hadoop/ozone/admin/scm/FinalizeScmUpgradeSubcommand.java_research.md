<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/FinalizeScmUpgradeSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/FinalizeScmUpgradeSubcommand.java

Purpose: Starts and monitors SCM upgrade finalization, paralleling the OM finalization command but using `ScmClient`.

Important APIs and types: `ScmClient.finalizeScmUpgrade`, `queryUpgradeFinalizationProgress`, `UpgradeFinalization` helpers/emitters, `StatusAndMessages`, `UpgradeException`, `ExecutorService`, and `Future`.

Control flow: `execute()` creates an upgrade client ID and calls `finalizeScmUpgrade`. Already finalized prints and exits; a non-starting response prints invalid status and throws IOException; `UpgradeException` is passed to shared invalid-request handling with the takeover flag. It then monitors progress in a single-thread executor, polling every 500 ms, printing messages for in-progress/done states, handling already-finalized takeover, and emitting finished/cancel/error messages.

State and persistence behavior: No local persistence. Remote SCM finalization mutates SCM metadata layout and feature finalization state.

Dependencies and integration points: Registered below `ScmAdmin`; shares finalization messaging conventions with OM and Ozone upgrade utilities.

Risks: Monitoring can run indefinitely until server status changes. Execution exceptions are wrapped in IOException. The command continues to monitor after handled `UpgradeException`, relying on shared handler semantics.

Test signals: Start/finalized/invalid response paths, takeover handling, message streaming, exception wrapping, cancellation/interruption, and emitted component name `Storage Container Manager`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/FinalizeScmUpgradeSubcommand.java -->
