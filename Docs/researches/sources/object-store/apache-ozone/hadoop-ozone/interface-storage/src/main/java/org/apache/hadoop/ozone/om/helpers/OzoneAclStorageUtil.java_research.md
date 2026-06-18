# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneAclStorageUtil.java

Purpose: Package-private list conversion utility for ACL storage protobufs.

Important APIs/types/functions: `toProtobuf(List<OzoneAcl>)` maps each runtime ACL through `OzoneAclStorage.toProtobuf`. `fromProtobuf(List<OzoneAclInfo>)` maps each proto ACL through `OzoneAclStorage.fromProtobuf`.

Control flow, state, and persistence: Stateless helper. It preserves list order while converting between Java and persisted proto ACL representations.

Dependencies and integration points: Used by `OmPrefixInfo` serialization/deserialization. Depends on `OzoneAcl`, `OzoneAclInfo`, and `OzoneAclStorage`.

Risks: No null checks are present for the list or elements, so callers must provide valid lists. It allocates mutable `ArrayList`s, but callers such as `OmPrefixInfo` later wrap state immutably.

Test signals: Indirectly covered by prefix info tests and prefix codec round trips.
