## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/prefix/OMPrefixRemoveAclRequest.java

Purpose: `OMPrefixRemoveAclRequest` removes one ACL from a prefix resource. It supplies remove-specific parsing, response, audit, and `PrefixManagerImpl` invocation.

Important APIs/types/functions: The constructor parses `RemoveAclRequest`, stores an `OzoneObj`, and wraps the single `OzoneAcl` in a list. `apply` calls `prefixManager.removeAcl(resolvedOzoneObj, ozoneAcls.get(0), omPrefixInfo)`. `onSuccess` builds `RemoveAclResponse`; `onFailure` returns `OMPrefixAclResponse`.

Control flow: The base class resolves, validates, authorizes, locks, and reads prefix info. This subclass removes the ACL if present. If the resulting `OmPrefixInfo` has no ACLs, the base class tombstones the prefix table row.

State and persistence behavior: Prefix ACL removal is staged in the prefix table cache. Remove-to-empty deletes the prefix info row. Operation result false indicates the ACL was absent rather than a request failure. Audit uses `OMAction.REMOVE_ACL` with the ACL string.

Dependencies and integration points: It integrates with prefix manager removal semantics, prefix table cache replay, audit logging, and native ACL checks from the base class.

Risks and edge cases: Removing from a missing prefix can lead to `PREFIX_NOT_FOUND` if the prefix manager returns no info. Empty ACL cleanup must stay aligned with prefix manager behavior. The transaction ID is not passed to `removeAcl`, unlike add/set, so update-ID handling depends on surrounding base logic and manager implementation.

Test signals: Cover removing present and absent ACLs, deleting the prefix row when ACLs become empty, linked-bucket prefixes, missing prefix info, and response/audit behavior.
