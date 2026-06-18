## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/prefix/OMPrefixAddAclRequest.java

Purpose: `OMPrefixAddAclRequest` adds one ACL to a prefix resource. It parses the protobuf add request and delegates validation, locking, and persistence to `OMPrefixAclRequest`.

Important APIs/types/functions: The constructor reads `AddAclRequest`, converts the target with `OzoneObjInfo.fromProtobuf`, and converts the ACL with `OzoneAcl.fromProtobuf`. `apply` invokes `prefixManager.addAcl(resolvedOzoneObj, ozoneAcl, omPrefixInfo, trxnLogIndex)`. `onSuccess` builds `AddAclResponse`, and `onFailure` returns `OMPrefixAclResponse`.

Control flow: After the base class resolves and locks the prefix, this class asks `PrefixManagerImpl` to add the ACL and returns the operation result. Completion logs whether the ACL was newly added or already present.

State and persistence behavior: The resulting `OmPrefixInfo` is cached by the base class in the prefix table. If the ACL already exists, operation result is false but the request is not exceptional. Audit records `OMAction.ADD_ACL` and includes the ACL.

Dependencies and integration points: It relies on `PrefixManagerImpl.addAcl`, prefix table replay through `OMPrefixAclResponse`, Ozone ACL/object protobuf conversions, and audit logging.

Risks and edge cases: Prefix manager must handle creation of a new prefix row when adding the first ACL. Duplicate ACLs return false. Linked-bucket resolution means logged/audited path should reflect the resolved prefix object from the base class.

Test signals: Cover adding a first prefix ACL, adding a duplicate, linked bucket prefixes, invalid prefix paths via base validation, response replay, and audit output.
