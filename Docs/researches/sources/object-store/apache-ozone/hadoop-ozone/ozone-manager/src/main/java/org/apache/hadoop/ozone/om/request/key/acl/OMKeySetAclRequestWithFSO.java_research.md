## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeySetAclRequestWithFSO.java

Purpose: `OMKeySetAclRequestWithFSO` replaces ACL lists on FSO file and directory targets. It supplies set-specific behavior to `OMKeyAclRequestWithFSO`.

Important APIs/types/functions: It parses `SetAclRequest`, converts all ACL protobuf entries via `OzoneAclUtil.fromProtobuf`, stamps modification time in `preExecute`, replaces ACLs through `builder.acls().set(ozoneAcls)`, and returns `OMKeyAclResponseWithFSO` for FSO replay.

Control flow: The FSO base request resolves and authorizes the path, loads an `OzoneFileStatus`, builds a leaf-name `OmKeyInfo`, invokes this set operation, and writes a file or directory cache entry. This class fills `SetAclResponse.response` with the operation result.

State and persistence behavior: The new ACL list is staged in the appropriate FSO table cache at the transaction index. The FSO base updates modification time when the set request has an object, matching the current code regardless of operation result.

Dependencies and integration points: It integrates with FSO directory/file tables, metrics, audit, `OzoneObjInfo`, `OzoneAclUtil`, and `OMKeyAclResponseWithFSO`.

Risks and edge cases: Full replacement is more destructive than add/remove. Directory handling depends on the FSO response and table routing. The modification-time behavior differs subtly from add/remove because it is not guarded by `operationResult` in the FSO base.

Test signals: Cover replacing ACLs on files and directories, nested paths, empty ACL list behavior, response replay, modification time, metric increment, and audit output.
