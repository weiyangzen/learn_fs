# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOzoneAclUtil.java

Purpose: tests ACL list mutation helpers in `OzoneAclUtil`, including add/remove semantics, null handling, merging permissions, and scope separation.

Important APIs/types/functions: exercises `OzoneAclUtil.addAcl`, `removeAcl`, `OzoneAcl.of`, `OzoneAcl.parseAcl`, `getAclList`, `isSet`, `getAclScope`, `getAclByteString`, and default rights from `OmConfig`.

Control flow and state: default ACLs are built from current user and groups with configured user/group default rights. Add tests merge new permissions into existing ACL entries and avoid duplicate entries. Remove tests handle null lists, missing entries, missing permissions, removal of newly added permissions, and full entry removal.

Dependencies and integration points: depends on `UserGroupInformation`, `OzoneConfiguration.newInstanceOf(OmConfig.class)`, ACL identity/scope/type enums, and Java list mutation. It is central to OM authorization metadata updates.

Risks and test signals: catches duplicate ACL entries, permission-bit removal errors, null list behavior, and accidental merging between `ACCESS` and `DEFAULT` scope ACLs. Scope test confirms same identity and rights can coexist separately by scope.
