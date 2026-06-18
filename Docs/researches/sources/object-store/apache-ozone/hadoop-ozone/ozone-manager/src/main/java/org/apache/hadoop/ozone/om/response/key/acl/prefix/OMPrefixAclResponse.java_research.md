# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/acl/prefix/OMPrefixAclResponse.java

Purpose: `OMPrefixAclResponse` persists ACL changes for prefix ACL entries.

Important APIs and types: It extends `OMClientResponse`, stores `OmPrefixInfo`, cleans `PREFIX_TABLE`, and checks whether the response has a remove-ACL response.

Control flow: On DB batch application, if the operation is remove ACL and the resulting ACL list is empty, it deletes the prefix row. Otherwise it writes the prefix info.

State and persistence behavior: It creates, updates, or deletes prefix-table ACL metadata.

Dependencies and integration points: It integrates prefix ACL request handlers, prefix table storage, and response success gating from `OMClientResponse`.

Risks and test signals: Tests should cover removing the last ACL deletes the row, removing one of many updates the row, add/set writes rows, and failed response no-op.
