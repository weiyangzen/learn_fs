## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeySetAclRequest.java

Purpose: `OMKeySetAclRequest` replaces the full ACL list on a key in non-FSO layouts. It provides set-specific protobuf parsing, response, audit, metrics, and old-client validation around `OMKeyAclRequest`.

Important APIs/types/functions: `preExecute` stamps `SetAclRequest.modificationTime`. The constructor parses `OzoneObjInfo` and converts the repeated ACL protobuf list through `OzoneAclUtil.fromProtobuf`. `apply` calls `builder.acls().set(ozoneAcls)`. `onSuccess` builds `SetAclResponse`, and `blockSetAclWithBucketLayoutFromOldClient` performs layout compatibility validation.

Control flow: The base class validates and locks the target key, then this class replaces its ACL collection. Set typically returns true from the ACL collection setter, and the response success/response fields mirror that boolean.

State and persistence behavior: The whole ACL list is written into the updated `OmKeyInfo` cache entry. Modification time is copied from the request when the operation result is true. Metrics increment through `incNumSetAcl`; audit uses `OMAction.SET_ACL` and includes the complete ACL list.

Dependencies and integration points: It relies on the base key ACL path, Ozone ACL utilities, request validators, metrics, audit, and `OMKeyAclResponse`.

Risks and edge cases: Replacing the list can remove implicit or inherited-looking ACLs if callers pass an incomplete list. Empty lists are possible and should be treated according to ACL collection semantics. Old-client layout gating must remain aligned with bucket layout support.

Test signals: Verify complete ACL replacement, empty-list behavior if allowed, missing key, authorization failure, modification time, audit list content, metric increment, and old-client layout rejection.
