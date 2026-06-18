<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestRequestContext.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestRequestContext.java

Purpose: validates `RequestContext` builder defaults, optional policy/S3 fields, recursive access flag, and `toBuilder` copy/modify behavior.

Important APIs and functions: `testRecursiveAccessFlag`, `testSessionPolicy`, `testToBuilderWithNoModifications`, and `testToBuilderWithModifications`.

Control flow: tests build default contexts, toggle `setRecursiveAccessCheck`, set session policy JSON strings, build a fully populated context, call `toBuilder`, and compare every preserved field. Modification tests create a second context from `toBuilder` with changed host, UGI, ACL rights, owner, recursive flag, session policy, and S3 action while asserting the original remains unchanged.

State and persistence behavior: immutable built contexts are the central state. No external persistence occurs. The test verifies copied fields include host, IP default, client UGI, service id, ACL identity/type, owner, recursive flag, session policy, and S3 action.

Dependencies and integration: `UserGroupInformation`, `IAccessAuthorizer` enums, JUnit assertions. Risks include accidental shallow mutation in builder reuse or future fields omitted from `toBuilder`. Test signal is strong for builder immutability and field preservation but does not parse or validate policy JSON.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestRequestContext.java -->
