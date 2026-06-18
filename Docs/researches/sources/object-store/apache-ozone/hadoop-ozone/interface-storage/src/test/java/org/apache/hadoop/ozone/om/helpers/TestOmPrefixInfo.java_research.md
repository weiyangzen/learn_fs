# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmPrefixInfo.java

Purpose: Unit tests for `OmPrefixInfo` object semantics and protobuf conversion.

Important APIs/types/functions: Helpers build test `OzoneAclInfo`, metadata `KeyValue`, persisted prefix info, and runtime `OmPrefixInfo`. Tests cover `copyObject`, ACL immutability, `getFromProtobuf` with metadata/ACL, and `getProtobuf`.

Control flow, state, and persistence: The tests construct runtime and proto prefix representations, verify equality/copy isolation, assert that returned ACL list is immutable, and verify metadata/ACL counts and names across conversion.

Dependencies and integration points: Uses `OzoneAcl`, `IAccessAuthorizer`, `OzoneManagerStorageProtos.PersistedPrefixInfo`, HDDS `KeyValue`, and JUnit. It validates prefix table value conversion behavior.

Risks: Tests one ACL and one metadata entry; broader edge cases such as empty ACL rights, multiple ACL scopes, and object/update id compatibility are not fully covered.

Test signals: Strong focused signal for `OmPrefixInfo` immutability and proto conversion basics.
