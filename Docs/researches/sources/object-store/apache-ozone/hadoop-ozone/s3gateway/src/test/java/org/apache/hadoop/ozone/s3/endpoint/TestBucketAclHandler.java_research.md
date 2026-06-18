
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketAclHandler.java

Purpose: focused tests for `BucketAclHandler` dispatch and ACL handling.

Important APIs and control flow: setup builds the handler with stub client/headers and default `?acl`. PUT tests verify handler returns null without `?acl`, succeeds for all supported grant headers and multiple headers, rejects unsupported grantee URI/email types, throws for nonexistent buckets, accepts valid XML body, rejects invalid header format, supports multiple grantees in one header, and replaces existing ACLs. GET tests verify null without `?acl`, success with `?acl`, bucket-not-found exception, and returned ACL structure after setting a grant. `mockContext` supplies an `S3RequestContext` backed by a mocked bucket endpoint/volume.

State, dependencies, integration: uses in-memory bucket state and mocked context wrappers. Integrates handler-level logic independently from `BucketEndpoint`.

Risks and test signals: some bucket-not-found tests expect raw `OMException`, while endpoint-level tests expect S3-mapped exceptions; this distinction matters for layering. Tests validate dispatch contract where returning `null` means another handler should process the request.
