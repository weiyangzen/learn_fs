# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/upgrade/TestReconLayoutVersionManager.java

Purpose: Tests `ReconLayoutVersionManager`, which tracks Recon metadata layout version (MLV), software layout version (SLV), registered layout features, and transactional finalization of upgrade actions.

Important APIs and control flow: Setup mocks `ReconSchemaVersionTableManager`, static `ReconLayoutFeature.values`, a `DataSource`, and `Connection`. Tests verify initialization MLV/SLV, finalizing schema versions, registered-feature listing, no-feature no-op, rollback on upgrade action failure, rollback on schema update failure, version-sorted action order despite unsorted enum array, no-op when no upgrades are needed, and adding a later feature without re-running already finalized ones.

State and persistence behavior: Persistent state is represented by schema version table manager calls inside a JDBC transaction. Connection auto-commit is disabled, commits happen on success, and rollback is expected on failure. In-memory MLV should not advance when finalization fails.

Dependencies and integration points: Uses `ReconLayoutFeature`, `ReconUpgradeAction`, `ReconSchemaVersionTableManager`, `ReconContext`, JDBC `DataSource`/`Connection`, and Mockito static enum mocking. This governs execution of all Recon schema upgrade actions.

Risks and test signals: High signal for ordering and transaction semantics. Heavy static mocking can hide enum-specific production metadata issues, but it makes the version-manager algorithm deterministic and focused.
