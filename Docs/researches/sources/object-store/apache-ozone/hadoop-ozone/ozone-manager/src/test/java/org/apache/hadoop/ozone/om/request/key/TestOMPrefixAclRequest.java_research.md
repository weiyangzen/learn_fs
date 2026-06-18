# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMPrefixAclRequest.java

Purpose: tests prefix ACL request handling for `AddAcl`, `RemoveAcl`, and `SetAcl` OM requests targeting `OzoneObj.ResourceType.PREFIX`. It ensures prefix ACL mutations update both the in-memory `PrefixManagerImpl` prefix tree and the metadata-manager prefix table cache.

Important APIs and types: `OMPrefixAddAclRequest`, `OMPrefixRemoveAclRequest`, `OMPrefixSetAclRequest`, `PrefixManagerImpl`, `OmPrefixInfo`, `OzoneObjInfo`, `OzoneAcl`, and protobuf `AddAclRequest`, `RemoveAclRequest`, and `SetAclRequest`. Helper builders create prefix `OzoneObj` values using the current test volume and bucket, then embed ACL protobufs into `OMRequest` instances.

Control flow: each positive test wires a real `PrefixManagerImpl` into the mocked `OzoneManager`, creates volume/bucket metadata, builds a prefix path with trailing slash, runs request `preExecute`, and calls `validateAndUpdateCache` with monotonically increasing transaction IDs. Add ACL is exercised twice to verify idempotent ACL membership while still refreshing update ID. Remove ACL first removes a non-existent ACL from an existing prefix, then removes the existing ACL and validates prefix deletion, then attempts removal from a non-existent prefix. Set ACL creates or replaces the prefix ACL list and verifies repeated set updates the transaction ID.

State and persistence behavior: success paths read `prefixManager.getPrefixInfo`, `prefixManager.getAcl`, and `omMetadataManager.getPrefixTable().get(prefixObj.getPath())`. Add/set retain a prefix-table row with `name == prefix path` and transaction-aligned `updateID`. Removing the last ACL removes the prefix from both the tree and table, while removing a missing ACL from an existing prefix only updates the `updateID`.

Dependencies and integration points: validates path normalization expected by ACL code. Invalid requests without a trailing slash or with a malformed filesystem path (`/dir1//dir2/`) return `INVALID_PATH_IN_ACL_REQUEST`.

Risks covered: divergence between prefix manager and table cache, non-idempotent duplicate ACL behavior, stale update IDs after no-op ACL changes, and incorrect status for absent prefixes. The tests do not exercise batch commit, audit logs, or ACL authorization; they focus on cache/table mutation semantics.

Test signals: expected statuses are `OK`, `INVALID_PATH_IN_ACL_REQUEST`, and `PREFIX_NOT_FOUND`; ACL lists have exact sizes and entries; removed prefixes return null `OmPrefixInfo` and empty ACL lists.
