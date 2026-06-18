## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyRemoveAclRequest.java

Purpose: `OMKeyRemoveAclRequest` removes a single ACL from a key in non-FSO layouts. It is operation-specific glue around `OMKeyAclRequest`.

Important APIs/types/functions: `preExecute` stamps `RemoveAclRequest.modificationTime`. The constructor parses the request object and ACL. `apply` calls `builder.acls().remove(ozoneAcls.get(0))`. `onSuccess` builds `RemoveAclResponse`. `blockRemoveAclWithBucketLayoutFromOldClient` rejects unsupported old-client layout combinations.

Control flow: The base class validates the object path, authorizes WRITE_ACL, locks the bucket, fetches the key, and invokes remove. A missing ACL produces `operationResult=false` and a successful request with response false; a missing key or invalid path fails the request.

State and persistence behavior: Successful key lookup leads to a cache update of the `OmKeyInfo` with new update ID. Modification time is updated only when the ACL was actually removed. Metrics increment through `incNumRemoveAcl`, and audit records `OMAction.REMOVE_ACL`.

Dependencies and integration points: The class depends on `OzoneAcl` conversion, Ozone audit constants, `OmResponseUtil`, old-client request validation, and the base key ACL cache-update path.

Risks and edge cases: The operation is idempotent at ACL level: absent ACL is not exceptional. Only one ACL is processed. Old-client validators must parse volume and bucket from the same object path format the runtime parser accepts.

Test signals: Verify remove-present, remove-absent, missing-key, authorization failure, old-client layout validation, modification time behavior, metric increment, and audit ACL text.
