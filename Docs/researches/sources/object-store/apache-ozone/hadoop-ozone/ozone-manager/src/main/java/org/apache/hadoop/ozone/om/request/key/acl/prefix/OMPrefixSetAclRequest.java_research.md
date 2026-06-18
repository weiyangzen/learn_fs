## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/prefix/OMPrefixSetAclRequest.java

Purpose: `OMPrefixSetAclRequest` replaces the ACL list on a prefix resource. It is the set operation implementation for the prefix ACL request hierarchy.

Important APIs/types/functions: The constructor parses `SetAclRequest`, converts the target `OzoneObj`, and builds a mutable `List<OzoneAcl>` from all protobuf ACL entries. `apply` calls `prefixManager.setAcl(resolvedOzoneObj, ozoneAcls, omPrefixInfo, trxnLogIndex)`. `onSuccess` builds `SetAclResponse`.

Control flow: The base class resolves and locks the prefix, then this class asks the prefix manager to replace the ACL list. Completion logs success or failure and always includes the full ACL list in the audit map when present.

State and persistence behavior: The returned `OmPrefixInfo` is cached by the base class. Unlike remove-to-empty, set uses the normal update path even if the list is empty unless prefix manager returns a different state. Audit uses `OMAction.SET_ACL`.

Dependencies and integration points: It depends on `PrefixManagerImpl.setAcl`, `OMPrefixAclResponse`, Ozone ACL protobuf conversion, and the base prefix ACL validation/locking path.

Risks and edge cases: Full replacement can unintentionally clear existing prefix ACLs. Empty set behavior should be explicitly tested because the base class only tombstones on remove requests. Linked-bucket resolution affects the actual prefix row modified.

Test signals: Cover replacing multiple prefix ACLs, setting an empty list if valid, linked-bucket prefix resolution, invalid paths, response replay, and audit content.
