# sources/sync-backup/kopia/repo/maintenance/maintenance_quick_test.go

Purpose: verifies quick maintenance behavior when the epoch manager is enabled.

Important APIs/types/functions: `TestQuickMaintenanceRunWithEpochManager`, `TestQuickMaintenanceAdvancesEpoch`, `setRepositoryOwner`, `verifyEpochManagerIsEnabled`, and `verifyEpochTasksRunsInQuickMaintenance`.

Control flow: tests create format v3 repositories, set maintenance owner, verify epoch manager availability, run quick snapshot maintenance, and assert schedule entries for epoch compaction and advancement. The second test writes enough index blobs and advances fake time to force epoch advancement.

State/persistence behavior: writes repository objects/index blobs, maintenance params, and encrypted maintenance schedules; verifies write epoch changes after maintenance.

Dependencies/integration: uses `repotesting`, `faketime`, `epoch.Manager`, object writers, and `snapshotmaintenance.Run`.

Risks/test signals: catches regressions where quick maintenance bypasses epoch tasks or fails to advance eligible write epochs. It is format-version specific.
