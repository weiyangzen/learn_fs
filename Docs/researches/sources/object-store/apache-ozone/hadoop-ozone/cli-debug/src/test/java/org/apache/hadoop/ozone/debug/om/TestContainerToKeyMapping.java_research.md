# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/om/TestContainerToKeyMapping.java

Purpose: `TestContainerToKeyMapping` verifies the offline OM container-to-key mapping command across FSO keys, OBS keys, open keys, multipart uploads, absent containers, and unreferenced FSO files.

Important APIs and types: It uses `OmMetadataManagerImpl`, `OzoneDebug`, `CommandLine`, temp OM DB paths, `OmVolumeArgs`, `OmBucketInfo`, `OmDirectoryInfo`, `OmKeyInfo`, `OmKeyLocationInfo`, `OmMultipartKeyInfo`, `StandaloneReplicationConfig`, and protobuf `PartKeyInfo`.

Control flow: Setup creates an `om.db`, redirects command output, populates volume/bucket/directory/file/key/open-key/multipart tables with synthetic metadata and block locations, then closes the store. Each test executes `om container-key-mapping --db <path> --containers ...` with relevant flags and asserts the emitted JSON contains expected paths, container IDs, `openKeys`, `totalKeys`, or `unreferencedKeys`.

State and persistence behavior: Test state is a temporary RocksDB OM metadata store. It creates both FSO and OBS bucket metadata, committed keys, open keys, multipart entries, and an intentionally missing parent directory. Cleanup closes the store if still open.

Dependencies and integration points: This is the strongest local signal for `ContainerToKeyMapping`; it exercises real OM table codecs and command dispatch through `OzoneDebug`.

Risks: Assertions are substring-based rather than full JSON structural checks. It does not test invalid input, duplicate containers, or cleanup of the temporary `omdirtree.db` after command failure.

Test signals: Required signals are full FSO path reconstruction, OBS database-key output, filename-only mode, open-key inclusion, MPU inclusion, zero result for nonexistent container, and unreferenced count for missing FSO parent.
