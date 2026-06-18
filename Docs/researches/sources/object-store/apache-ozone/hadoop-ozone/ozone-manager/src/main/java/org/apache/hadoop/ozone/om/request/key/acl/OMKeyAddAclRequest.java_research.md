## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyAddAclRequest.java

Purpose: `OMKeyAddAclRequest` implements add-ACL for key resources in non-FSO layouts. It parses the protobuf `AddAclRequest`, stores the target `OzoneObj`, key path, and single ACL, and delegates common validation and cache mutation to `OMKeyAclRequest`.

Important APIs/types/functions: `preExecute` stamps `modificationTime` with `Time.now()` and user info. The constructor reads `OzoneObjInfo.fromProtobuf`, `OzoneAcl.fromProtobuf`, and calls `initializeBucketLayout`. `apply` calls `builder.acls().add(ozoneAcls.get(0))`. `onSuccess` creates `AddAclResponse`, and `blockAddAclWithBucketLayoutFromOldClient` validates old-client requests against bucket layout.

Control flow: During validate/update, the base class locates the key and invokes `apply`. If the ACL did not already exist, `operationResult` is true, the updated key receives the preExecute modification time, and the response success flag is true. If the ACL exists, response success is false but the request still completes without exception.

State and persistence behavior: The request updates the key-table cache with a new `OmKeyInfo` when the target key exists. It increments the add-ACL metric before delegating. Audit logging includes `OMAction.ADD_ACL` and adds the ACL list string to the audit map.

Dependencies and integration points: It depends on the key ACL base class, protobuf ACL/object conversions, metrics, audit, and request validators for older clients. Bucket-layout validation prevents old clients from operating on non-legacy layouts without layout-aware request handling.

Risks and edge cases: Only the first ACL in `ozoneAcls` is applied because add-ACL is a single-ACL operation. Existing ACLs produce a false response rather than an exception. Constructor layout discovery can fall back if the bucket lookup fails.

Test signals: Tests should cover adding a new ACL, adding a duplicate ACL, missing key failures, old-client layout validation, metric increments, modification time updates, and audit map content.
