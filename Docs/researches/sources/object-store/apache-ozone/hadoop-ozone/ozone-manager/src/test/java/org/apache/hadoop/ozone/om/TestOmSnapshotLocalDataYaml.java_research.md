# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOmSnapshotLocalDataYaml.java

Purpose: Tests YAML serialization/deserialization for `OmSnapshotLocalData`, including checksum handling, version/SST metadata, transaction info, and backward-compatible missing fields.

Important APIs and types: `OmSnapshotLocalData`, `OmSnapshotLocalDataYaml.YamlFactory`, `YamlSerializer`, `ObjectSerializer`, `VersionMeta`, `SstFileInfo`, `LiveFileMetaData`, `TransactionInfo`, SnakeYAML `Yaml`, and `OzoneConsts` snapshot-local-data field constants.

Control flow: a shared serializer is created in `BeforeAll`. Helper `writeToYaml` builds snapshot local data from mocked RocksDB live-file metadata, sets version, flags, previous snapshot ID, transaction info, defrag time, needs-defrag flag, and defragged SST version entries, then saves YAML. Tests load and compare the object graph, update and resave data, validate empty-file failure, verify checksum, check field names in raw YAML, and mutate YAML to simulate legacy missing/empty `lastDefragTime`.

State and persistence: writes real YAML files under a test root and deletes them after each test. The serialized state includes snapshot UUIDs, previous snapshot UUID, DB sequence number, transaction info, checksum, SST filtered/defrag flags, last defrag time, and versioned SST file lists.

Dependencies and integration points: integrates with snapshot local data management and RocksDB SST metadata filtering. The exact YAML keys are a compatibility surface for persisted snapshot sidecar files.

Risks and edge cases: version numbering changes during serialization (`42` becomes expected current versions `43/44` in the metadata map); checksum computation must ignore its own checksum field; legacy YAML without last-defrag-time must still load; empty YAML must fail loudly.

Test signals: exact `VersionMeta` map equality, checksum presence and verification, raw YAML containing all current constants, updated flags and transaction info after save/load, IOException message for empty file, and default `lastDefragTime=0` for missing or empty legacy values.
