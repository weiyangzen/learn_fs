# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneAclStorage.java

Purpose: Package-private converter between runtime `OzoneAcl` objects and storage-layer protobuf `OzoneAclInfo`.

Important APIs/types/functions: Static `toProtobuf(OzoneAcl)` writes name, identity type, scope, and rights bytes. Static `fromProtobuf(OzoneAclInfo)` reconstructs a BitSet of ACL rights, maps bit indices to `IAccessAuthorizer.ACLType`, builds an `EnumSet`, and creates an `OzoneAcl`.

Control flow, state, and persistence: Stateless conversion helper. It defines the byte-level ACL rights persistence bridge for prefix metadata and other storage proto users.

Dependencies and integration points: Used by `OzoneAclStorageUtil` and `OmPrefixInfo`. Depends on `OzoneAcl`, `AclScope`, `IAccessAuthorizer`, and `OzoneManagerStorageProtos.OzoneAclInfo`.

Risks: Enum name and ordinal stability are critical. Rights bytes are decoded by ACLType ordinal via `BitSet.stream()`, so reordering ACLType values or adding incompatible positions can corrupt interpretation. `EnumSet.copyOf` on an empty list can throw, so empty rights may need upstream handling.

Test signals: Covered indirectly by `TestOmPrefixInfo` and `TestOmPrefixInfoCodec`, which serialize and deserialize ACL-bearing prefix info.
