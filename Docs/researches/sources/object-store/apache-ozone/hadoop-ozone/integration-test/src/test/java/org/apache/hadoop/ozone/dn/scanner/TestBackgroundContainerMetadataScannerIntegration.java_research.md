# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/scanner/TestBackgroundContainerMetadataScannerIntegration.java

Purpose: Integration tests for `BackgroundContainerMetadataScanner`, the fast metadata-only scanner that detects obvious container metadata corruption in both open and closed containers.

Important APIs, types, and functions: Extends `TestContainerScannerIntegrationAbstract`. Uses `ReplicationManager.ReplicationManagerConfiguration`, `ContainerScannerConfiguration`, `BackgroundContainerMetadataScanner`, `TestContainerCorruptions`, and `ContainerLogger` log capture. `supportedCorruptionTypes` excludes missing/corrupt/truncated block data because this scanner checks metadata, not data contents.

Control flow: Setup shortens the replication manager interval, enables scrubbing, disables the data scanner to isolate metadata scanner behavior, shortens metadata scan interval, and builds the single-datanode cluster. The test writes one closed and one open container, records initial closed checksum and verifies open checksum is zero, applies each supported metadata corruption to both containers, waits for both local states to become `UNHEALTHY`, waits for SCM reports, asserts closed checksum did not change, checks whether the open container gets a checksum depending on whether metadata/container directory was missing, waits for SCM to close the open container, and verifies one log event for each container.

State and persistence behavior: Metadata corruption mutates container metadata files/directories. The metadata scanner changes container state to unhealthy but does not itself generate data checksums; checksum generation for open containers happens as a side effect of marking the container unhealthy when possible. SCM lifecycle state for the open container transitions away from open after unhealthy reporting.

Dependencies and integration points: Ties datanode metadata scanner, SCM replica/lifecycle state, replication manager closure behavior, checksum generation side effects, and corruption logging.

Risks: The test relies on disabled data scanner so data corruption does not mask metadata scanner signals. SCM lifecycle closure after unhealthy report is asynchronous. Missing metadata/container directory cases require special checksum expectations.

Test signals: Local container state and SCM replica state must become `UNHEALTHY`, closed checksum remains stable, open checksum behavior matches corruption type, SCM closes the open container, and logs contain exactly one corruption signal per container.
