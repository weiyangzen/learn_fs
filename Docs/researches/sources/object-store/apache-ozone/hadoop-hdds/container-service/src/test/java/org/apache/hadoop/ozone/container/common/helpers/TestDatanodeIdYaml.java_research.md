# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/helpers/TestDatanodeIdYaml.java

Purpose: This suite verifies YAML serialization and deserialization of `DatanodeDetails`, especially layout-version-gated port compatibility for Ratis datastream and web UI ports.

Important APIs and types: It uses `DatanodeIdYaml.createDatanodeIdFile`, `DatanodeIdYaml.readDatanodeIdFile`, `MockDatanodeDetails.randomDatanodeDetails`, `DatanodeLayoutStorage`, `HDDSLayoutFeature`, `DatanodeDetails.Port.Name`, and `OzoneConfiguration`.

Control flow: `testWriteRead` writes random datanode details to `datanode.yaml` and checks object equality and debug string equality. Two Ratis datastream tests initialize layout storage before or after `RATIS_DATASTREAM_PORT_IN_DATANODEDETAILS` and verify fallback-to-Ratis-port or preservation of the separate datastream port. Two web UI tests initialize layout storage before or after `WEBUI_PORTS_IN_DATANODEDETAILS` and verify HTTP/HTTPS omission or preservation.

State and persistence behavior: The tests persist YAML ID files and layout storage state under a temp metadata directory. The read path changes output depending on persisted layout version, not only YAML content. This protects upgrade compatibility where older layout versions did not persist newer ports.

Dependencies and integration points: Datanode startup and identity recovery depend on these files. The tests integrate identity serialization with datanode layout storage and HDDS upgrade features.

Risks: Random datanode details include several port values, so assertions focus on compatibility-sensitive ports. Behavior before layout features intentionally discards or aliases newer ports, which can surprise code expecting all random details to round-trip exactly.

Test signals: Full equality for normal read/write, datastream port fallback before its layout feature, exact datastream preservation after the feature, HTTP/HTTPS null before web UI feature, and exact HTTP/HTTPS preservation after the feature.
