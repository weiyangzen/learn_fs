# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneDebugReplicasVerify.java

## Purpose
`TestOzoneDebugReplicasVerify` validates `ozone debug replicas verify` checksum behavior against real mini-cluster replicas, including valid input, missing option handling, corrupted block files, and truncated block files.

## Important APIs, Types, and Functions
The abstract test uses `NonHATests.TestCase`, `OzoneDebug`, `TestDataUtil.createKeys`, OM key metadata, `OmKeyLocationInfo`, datanode `ContainerSet`, and helper methods `findFirstBlockFile`, `corruptBlock`, `truncateBlock`, and `getFirstContainer`. It passes OM and SCM addresses through `--set=` arguments.

## Control Flow, State, and Persistence
Before each test, it creates ten keys and records a volume path for debug command input. Cleanup logs captured output and deletes generated keys, buckets, and volumes. The parameterized test verifies `replicas verify` without `--checksums` exits with code 2, and with `--checksums` exits zero and emits no corruption text. Corruption tests locate the first physical `.block` file under a container's `chunks` directory, corrupt or truncate it, execute `replicas verify --checksums --all-results`, and assert the expected diagnostic appears.

## Dependencies and Integration Points
This integrates debug CLI, OM/SCM client configuration, key location metadata, datanode on-disk chunk/block file layout, Xceiver client reads, checksum verification, and physical file mutation utilities.

## Risks and Test Signals
Risks include direct mutation of local replica files, assumptions about `.block` filenames containing local IDs, and cleanup needing to remove all created namespace objects. Signals are exit codes plus explicit output diagnostics: `Checksum mismatch` for corrupted files and `Unexpected read size` for truncated files.
