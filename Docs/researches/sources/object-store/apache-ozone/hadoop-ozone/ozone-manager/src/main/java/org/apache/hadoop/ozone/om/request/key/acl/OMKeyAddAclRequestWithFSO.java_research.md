## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyAddAclRequestWithFSO.java

Purpose: `OMKeyAddAclRequestWithFSO` implements add-ACL for FSO files and directories. It supplies add-specific parsing, response construction, metrics, logging, and audit on top of `OMKeyAclRequestWithFSO`.

Important APIs/types/functions: `preExecute` sets `AddAclRequest.modificationTime`. `apply` adds the first requested ACL to the key/directory ACL list. There are two `onSuccess` overloads: the inherited flat signature returns `OMKeyAclResponse`, while the FSO signature returns `OMKeyAclResponseWithFSO` with `isDir`, bucket layout, volume ID, and bucket ID.

Control flow: The base FSO class resolves the path, determines whether it is a file or directory, and invokes this class's add operation. This class sets response success and `AddAclResponse.response` to the boolean returned by the ACL list add.

State and persistence behavior: File and directory cache writes are handled by the FSO base class. This subclass increments `incNumAddAcl`, records operation logs, and emits `OMAction.ADD_ACL` audit entries containing the ACL string.

Dependencies and integration points: It integrates FSO ACL mutation with `OMKeyAclResponseWithFSO` replay, `OzoneObjInfo`, `OzoneAcl`, and OM metrics/audit. Unlike the non-FSO variant it receives bucket layout from the request factory rather than discovering it from metadata.

Risks and edge cases: Duplicate ACLs return false without failure. Directory targets must use the FSO success response so replay writes the directory table. The class still keeps the non-FSO `onSuccess` override for abstract compatibility; routing should ensure FSO paths use the FSO callback.

Test signals: Cover adding ACLs to nested FSO files, FSO directories, duplicate ACL attempts, response replay for directory versus file rows, modification time updates, and metric/audit output.
