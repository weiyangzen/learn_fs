<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/DatanodeIdYaml.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/DatanodeIdYaml.java

Purpose: YAML serializer/deserializer for `datanode.id`, converting between `DatanodeDetails` and a SnakeYAML-compatible bean while respecting HDDS layout-version gated ports.

Important APIs and control flow: `createDatanodeIdFile` builds a flow-style YAML writer, converts details through `getDatanodeDetailsYaml`, and delegates atomic-style dumping to `YamlUtils.dump`. `readDatanodeIdFile` loads `DatanodeDetailsYaml`, validates that UUID is present, rebuilds `DatanodeDetails` with UUID, host, IP, certificate serial, persisted operational state, state expiry, ports, and initial/current versions. The nested `DatanodeDetailsYaml` bean exposes getters and setters needed by SnakeYAML field introspection.

State and persistence: persisted fields are UUID, network identity, certificate serial, persisted op state and expiry, port map, and layout versions. `getDatanodeDetailsYaml` instantiates `DatanodeLayoutStorage` to filter out ports whose `DatanodeDetails.Port.Name` enum field has `BelongsToHDDSLayoutVersion` newer than the local layout.

Dependencies and integration: used by `ContainerUtils` for datanode ID read/write. It depends on `DatanodeLayoutStorage`, `HDDSLayoutFeature`, reflection on `DatanodeDetails.Port.Name`, `YamlUtils`, and protobuf `NodeOperationalState`.

Risks and test signals: malformed YAML, empty files, absent UUID, invalid UUID strings, invalid persisted op-state names, and unsupported port enum names should be covered. Reflection failures log and continue, which can silently omit layout filtering for unknown enum fields. Layout-gated ports need upgrade tests to ensure old layout versions do not persist ports that old software cannot read.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/DatanodeIdYaml.java -->
