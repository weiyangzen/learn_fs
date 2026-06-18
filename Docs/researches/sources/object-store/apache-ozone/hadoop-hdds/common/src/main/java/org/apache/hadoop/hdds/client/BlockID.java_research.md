## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/BlockID.java

Purpose: value object for an Ozone block identity: container ID, local ID, block commit sequence ID, and optional replica index.

Important APIs: constructors from container/local IDs, copy constructor, and `ContainerBlockID`; getters; mutable `setBlockCommitSequenceId`; string append; protobuf conversions for datanode `DatanodeBlockID` and HDDS `BlockID`; equality/hash including commit sequence ID and optional replica index.

Control flow: datanode proto conversion preserves replica index only when present; HDDS proto conversion does not carry replica index and rehydrates it as null. State/persistence: container block ID is final, BCS ID is mutable, replica index is final nullable state.

Dependencies: Jackson `JsonIgnore`, datanode and HDDS protobufs, `ContainerBlockID`. Integration points: container protocol, block allocation, SCM/OM metadata, and client/server serialization. Risks: mutating BCS ID after use in maps/sets breaks hash semantics; null replica index is intentionally distinct from zero; converting through HDDS proto drops replica index. Test signals: round trips through both protobuf forms, equality/hash with null vs zero replica index, and mutation safety expectations.
