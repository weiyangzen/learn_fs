# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/helpers/OmPrefixInfo.java

Purpose: Immutable persisted model for OM prefix path metadata, currently centered on prefix ACLs and metadata.

Important APIs/types/functions: `OmPrefixInfo` extends `WithObjectID` and implements `CopyObject<OmPrefixInfo>`. It exposes `getCodec()`, `getAcls()`, `getName()`, `newBuilder()`, `getProtobuf()`, `builderFromProtobuf()`, `getFromProtobuf()`, `copyObject()`, and `toBuilder()`. The nested `Builder` supports ACL set/add/remove operations, metadata addition, object/update id setters, validation, and `isAclsChanged()`.

Control flow, state, and persistence: The static codec is a `DelegatedCodec` over `Proto2Codec<PersistedPrefixInfo>`, so persisted bytes are `OmStorageProtocol.proto` `PersistedPrefixInfo`. `getProtobuf()` serializes name, ACLs, metadata, object ID, and update ID. Deserialization rebuilds metadata, ACL list, and optional object/update IDs. Internal ACL state is stored as a Guava `ImmutableList`.

Dependencies and integration points: Used by `OMMetadataManager.getPrefixTable()` for prefix ACL storage. Depends on `OzoneAcl`, `OzoneAclStorageUtil`, `KeyValueUtil`, HDDS DB codec interfaces, JCIP `@Immutable`, and `PersistedPrefixInfo`.

Risks: Builder validation requires a non-null name but does not validate path shape. ACL conversion depends on enum-name compatibility between `OzoneAcl` and storage proto. The object/update IDs are optional on read but always set on `getProtobuf()`, which can matter for compatibility with older records.

Test signals: `TestOmPrefixInfo` covers copy behavior, immutability, protobuf parsing, and protobuf generation. `TestOmPrefixInfoCodec` covers round-trip persisted-format codec behavior.
