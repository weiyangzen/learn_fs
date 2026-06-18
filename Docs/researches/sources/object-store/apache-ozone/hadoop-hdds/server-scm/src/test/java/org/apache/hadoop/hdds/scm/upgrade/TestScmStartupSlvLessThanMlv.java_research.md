# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/upgrade/TestScmStartupSlvLessThanMlv.java

Purpose: This downgrade-protection test verifies that SCM refuses to start when the metadata layout version recorded in its VERSION file is greater than the software layout version supported by the running binary.

Important APIs and types: It uses `StorageContainerManager`, `OzoneConfiguration`, `UpgradeTestUtils.createVersionFile`, `HDDSLayoutFeature`, `LayoutFeature`, `HddsProtos.NodeType.SCM`, `ScmConfigKeys.OZONE_SCM_DB_DIRS`, and `HddsConfigKeys.OZONE_METADATA_DIRS`. VERSION file properties include `SCM_ID` and `SCM_HA`.

Control flow: The test creates temporary SCM metadata, Ratis, and snapshot directories, computes `mlv` as one greater than the maximum known `HDDSLayoutFeature` layout version, writes an SCM VERSION file with that MLV, and asserts that constructing `StorageContainerManager` throws `IOException` with the exact expected message.

State and persistence behavior: Persistent state is the on-disk SCM `current/VERSION` file plus realistic Ratis directories used to simulate a newer prior SCM. Runtime behavior under test is startup validation in the version manager before SCM services are initialized.

Dependencies and integration points: This anchors upgrade/downgrade safety across SCM storage configuration, VERSION file parsing, HA metadata properties, and `StorageContainerManager` construction.

Risks: The test asserts the full exception message, so wording-only changes can fail it. It does not test a full cluster downgrade, only the constructor path after detecting `MLV > SLV`.

Test signals: The key signal is an `IOException` whose message includes the generated metadata layout version and current maximum software layout version.
