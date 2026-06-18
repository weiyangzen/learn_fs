<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerDataYaml.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerDataYaml.java

Purpose: YAML codec for `.container` metadata files, currently supporting key-value containers.

Important APIs and control flow: `createContainerFile` obtains the right YAML instance, computes and writes the metadata checksum, and dumps through `YamlUtils`. `readContainerFile`, `readContainer(byte[])`, and `readContainer(InputStream)` load YAML using field access and convert SnakeYAML failures or empty files to `IOException`. `getYamlForContainerType` builds a representer filtered to `KeyValueContainerData` YAML fields and optionally includes `replicaIndex`. The custom constructor maps the key-value YAML tag into `KeyValueContainerData`, manually restores DB type, metadata path, chunks path, metadata map, checksum, scan timestamp, state, schema version, and replica index. A custom integer constructor returns all YAML integers as `Long` to avoid type variance.

State and persistence: this file defines which `ContainerData` fields are persisted and how new fields must be explicitly restored. Null properties are omitted during dumping.

Dependencies and integration: used by container creation/update, `ContainerUtils` checksum verification, import/export packing, and persistence recovery. Depends on SnakeYAML internals, `KeyValueContainerData`, `OzoneConsts`, and protobuf container state.

Risks and test signals: any added YAML field requires updates to both the representer field list and constructor mapping. Tests should cover empty files, malformed YAML, missing required keys, replica index presence/absence, scan timestamp restoration, integer widths, and checksum round trips.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerDataYaml.java -->
