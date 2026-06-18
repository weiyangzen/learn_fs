# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/scanner/TestBackgroundContainerDataScannerIntegration.java

Purpose: Integration tests for `BackgroundContainerDataScanner`, which scans closed containers' data and metadata without client interaction and marks corrupted replicas unhealthy.

Important APIs, types, and functions: Extends `TestContainerScannerIntegrationAbstract`. Uses `ContainerScannerConfiguration`, `BackgroundContainerDataScanner`, `TestContainerCorruptions`, `ContainerChecksums`, `ContainerMerkleTreeTestUtils.readChecksumFile`, and `verifyAllDataChecksumsMatch`. Helper `assertReplicaChecksumMatches` compares SCM-reported checksum with the checksum tree written to disk.

Control flow: `init` enables container scrubbing, disables the metadata scanner to isolate data scanner behavior, shortens the data scan interval, and builds a one-datanode cluster. The parameterized test pauses scanning, writes and closes a container, verifies initial closed state and non-zero checksum, records the SCM-reported checksum, applies each corruption type, resumes scanning, waits for the container to become `UNHEALTHY`, and verifies SCM receives the unhealthy report. For missing metadata/container directories it expects the checksum to remain unchanged; for other corruption types it expects a new checksum, a rewritten checksum file, all data checksums to match, and corruption-specific log evidence.

State and persistence behavior: The scanner updates in-memory container state, writes checksum tree files for most corruptions, and updates SCM replica checksums via reports. Corruption mutates real container files, blocks, directories, or metadata under the temp datanode volume.

Dependencies and integration points: Integrates scanner scheduling, container state transitions, checksum file generation, SCM container replica reports, corruption helpers, and log validation.

Risks: Timing depends on scanner intervals and report propagation. Some corruptions intentionally prevent checksum tree writes, so expected behavior differs. Log assertion counts vary for block-level corruptions because multiple chunks can emit messages.

Test signals: Container state must move from `CLOSED` to `UNHEALTHY`; SCM replica state must match; data checksum must change or remain depending on corruption; checksum files and log messages provide secondary verification.
