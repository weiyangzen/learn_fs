<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMSnapshotProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMSnapshotProvider.java

Purpose: This test verifies `SCMSnapshotProvider` constructor validation for configured SCM HA Ratis storage and snapshot directories.

Important APIs and types: It uses `SCMSnapshotProvider`, `SCMHAUtils.getSCMRatisDirectory`, `SCMHAUtils.getSCMRatisSnapshotDirectory`, `OzoneConfiguration`, `HddsConfigKeys.OZONE_METADATA_DIRS`, `ScmConfigKeys.OZONE_SCM_HA_RATIS_STORAGE_DIR`, `OZONE_SCM_HA_RATIS_SNAPSHOT_DIR`, and a mocked `CertificateClient`.

Control flow: The success test creates both configured Ratis and snapshot directories and asserts the provider is constructed with the expected snapshot directory. Failure tests create only Ratis storage or no directories and assert `IllegalStateException` messages for missing snapshot or missing storage directories.

State and persistence behavior: Temporary directories are created under JUnit temp paths. No SCM DB or snapshot content is written.

Dependencies and integration points: This protects follower catch-up/snapshot-provider startup from silently using missing or wrong directories.

Risks: Constructor behavior is strict; deployments or tests that previously expected auto-create semantics would fail intentionally.

Test signals: Provider non-null with exact snapshot path, and exception messages containing "Ratis snapshot directory does not exist" or "Ratis storage directory does not exist".
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMSnapshotProvider.java -->
