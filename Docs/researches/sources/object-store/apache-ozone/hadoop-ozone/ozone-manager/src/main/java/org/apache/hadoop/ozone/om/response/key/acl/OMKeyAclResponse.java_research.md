# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/acl/OMKeyAclResponse.java

Purpose: `OMKeyAclResponse` persists ACL updates for keys in non-FSO layouts.

Important APIs and types: It extends `OmKeyResponse`, stores updated `OmKeyInfo`, cleans `KEY_TABLE`, and supports explicit bucket layout constructors.

Control flow: `addToDBBatch` derives the ozone key and writes updated key info to the key table.

State and persistence behavior: It updates key metadata ACL state only.

Dependencies and integration points: It is paired with key ACL request handlers and metadata-manager key routing.

Risks and test signals: Tests should cover add/remove/set ACL metadata persistence, failed response no-op behavior, and bucket layout selection.
