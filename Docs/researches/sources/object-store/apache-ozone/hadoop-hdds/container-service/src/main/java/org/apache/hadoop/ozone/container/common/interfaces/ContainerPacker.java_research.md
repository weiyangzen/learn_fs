<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerPacker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerPacker.java

Purpose: archive pack/unpack contract for moving complete container contents and descriptors through a single stream.

Important APIs and control flow: `unpackContainerData` extracts archive data to temporary and destination directories while returning the descriptor bytes instead of writing the descriptor. `pack` writes chunk data, metadata DB, and descriptor to a destination stream. `unpackContainerDescriptor` reads just the descriptor from an archive. Default `persistCustomContainerState` reads descriptor bytes through `ContainerDataYaml`, sets the target container state, and updates metadata at a custom metadata path.

State and persistence: implementations persist archive extraction outputs and descriptor state. The default method mutates container state and delegates persistence through `container.update`.

Dependencies and integration: used by `Container` import/export methods and handlers. Depends on `ContainerDataYaml` and protobuf container states.

Risks and test signals: archive tests should cover descriptor-only reads, partial extraction cleanup, custom state persistence, null descriptor handling, metadata preservation, and mismatches between descriptor metadata and target container paths. The default method reads original metadata but applies state to the target container data before update, so implementations must define update semantics clearly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerPacker.java -->
