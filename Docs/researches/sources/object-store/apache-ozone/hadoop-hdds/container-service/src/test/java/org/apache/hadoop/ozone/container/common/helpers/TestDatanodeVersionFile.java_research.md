# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/helpers/TestDatanodeVersionFile.java

Purpose: This suite verifies creation, reading, and validation of datanode volume VERSION files through `DatanodeVersionFile` and `StorageVolumeUtil`.

Important APIs and types: It uses `DatanodeVersionFile`, `DatanodeVersionFile.readFrom`, `StorageVolumeUtil.getStorageID`, `getClusterID`, `getDatanodeUUID`, `getCreationTime`, `getLayOutVersion`, `HDDSVolumeLayoutVersion.getLatestVersion`, and `InconsistentStorageStateException`.

Control flow: `setup` creates a VERSION file in a temp folder with random storage ID, cluster ID, datanode UUID, current creation time, and latest layout version, then reads properties back. `testCreateAndReadVersionFile` verifies all fields. Negative tests rewrite invalid values or pass a mismatched expected cluster ID and assert validation exceptions with expected message fragments.

State and persistence behavior: The persistent artifact is a Java properties VERSION file. The tests validate that IDs, creation time, and layout version survive round trip and that invalid/mismatched fields are rejected by storage utilities rather than silently accepted.

Dependencies and integration points: VERSION files are consumed by volume formatting, datanode startup, ID recovery, and storage consistency checks. This file complements `TestDatanodeLayOutVersion` by checking the layout version in persisted form.

Risks: Exact error-message fragments are asserted, so wording changes in validation exceptions can fail tests. The invalid layout version `100` assumes the version registry remains below that value.

Test signals: File existence, exact property round trip, mismatched cluster ID exception, negative creation time exception, and invalid layout version exception.
