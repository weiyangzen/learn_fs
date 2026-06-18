## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyRemoveAclRequestWithFSO.java

Purpose: `OMKeyRemoveAclRequestWithFSO` removes a single ACL from FSO file or directory targets. It specializes request parsing, response body, metrics, and audit while `OMKeyAclRequestWithFSO` handles path-ID-based lookup and persistence.

Important APIs/types/functions: `preExecute` sets remove modification time, `apply` removes the first ACL, and the FSO `onSuccess` returns `OMKeyAclResponseWithFSO`. It also provides the flat `onSuccess` required by the base abstract hierarchy.

Control flow: The FSO base class resolves linked buckets, checks WRITE_ACL, locates the path through `OMFileRequest`, and routes file versus directory cache writes. This subclass sets `RemoveAclResponse.response` to the removal boolean and logs whether an ACL was removed or absent.

State and persistence behavior: Mutation state is written to either the file table or directory table with the current transaction update ID. Modification time is updated only when removal succeeds. The response carries volume/bucket IDs and directory classification for replay.

Dependencies and integration points: It integrates with FSO metadata tables, `OzoneObjInfo`, `OzoneAcl`, OM metrics, and audit under `OMAction.REMOVE_ACL`.

Risks and edge cases: Removing a non-existent ACL is not an error. Directory targets rely on the FSO response class; using the generic response would miss directory-table persistence. The operation processes one ACL even though it stores a list wrapper.

Test signals: Tests should include ACL removal from FSO file and directory rows, absent ACL responses, missing path errors, nested paths, response replay, metrics, and audit output.
