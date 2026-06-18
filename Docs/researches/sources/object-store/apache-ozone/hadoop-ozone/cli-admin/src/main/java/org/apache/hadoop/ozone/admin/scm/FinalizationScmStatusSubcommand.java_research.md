<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/FinalizationScmStatusSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/FinalizationScmStatusSubcommand.java

Purpose: Queries SCM upgrade finalization status and prints the current status enum.

Important APIs and types: `ScmSubcommand`, `ScmClient.queryUpgradeFinalizationProgress`, `UpgradeFinalization.StatusAndMessages`, and UUID-generated upgrade client IDs.

Control flow: `execute()` creates a unique client ID, calls `queryUpgradeFinalizationProgress(upgradeClientID, false, true)`, and prints `progress.status()`.

State and persistence behavior: Read-only. It observes remote SCM finalization state and stores nothing locally.

Dependencies and integration points: Registered under `ScmAdmin`; mirrors the OM status command using SCM client APIs.

Risks: Only the enum is printed, not detailed messages. Parent field is unused.

Test signals: Verify query flags, status output, UUID client ID prefix, and IOException propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/FinalizationScmStatusSubcommand.java -->
