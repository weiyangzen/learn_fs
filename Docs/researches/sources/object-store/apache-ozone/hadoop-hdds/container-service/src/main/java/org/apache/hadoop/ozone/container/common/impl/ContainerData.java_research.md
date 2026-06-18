<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerData.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerData.java

Purpose: abstract in-memory representation of container metadata that is persisted in `.container` files and reported to SCM.

Important APIs and control flow: constructors initialize type, ID, layout version, metadata, OPEN state, max size, origin pipeline/node, zero checksum, and unset data checksum. Abstract hooks provide container paths, metadata paths, protobuf export, and BCSID. State methods are synchronized and include open/closing/closed/quasi/unhealthy checks plus transitions. Space accounting uses `commitSpace`, `releaseCommitSpace`, `incrWriteBytes`, and `updateWriteStats` to track committed volume bytes and used space. Checksum handling zeroes the checksum field, dumps YAML, and hashes the resulting metadata. Scan timestamp setters bridge serialized epoch milliseconds and transient `Optional<Instant>`.

State and persistence: persistent YAML fields include type, ID, layout version, state, metadata, max size, checksum, scan timestamp, origin pipeline, and origin node. Runtime-only state includes volume reference, statistics, committed-space flag, immediate close action flag, empty marker, replica index, and transient scan time.

Dependencies and integration: used by all container implementations, `ContainerDataYaml`, reports, scanners, deletion policies, dispatcher close logic, and volume accounting. Depends on `HddsVolume`, protobuf container messages, SnakeYAML, and `ContainerUtils`.

Risks and test signals: committed-space arithmetic must be tested around writes, overwrites that grow files, close transitions, and null volumes in tests. `getDataChecksum` returns 0 when unset, so callers must use `needsDataChecksum` if they need to distinguish absent checksum from real zero. YAML checksum stability depends on field order and representer behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerData.java -->
