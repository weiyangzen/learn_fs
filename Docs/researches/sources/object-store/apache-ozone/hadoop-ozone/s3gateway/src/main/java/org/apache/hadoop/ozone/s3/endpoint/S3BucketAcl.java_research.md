<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3BucketAcl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3BucketAcl.java

## Purpose
JAXB model for S3 `AccessControlPolicy` XML used by bucket and object ACL APIs.

## Important APIs, types, and functions
- Root fields are `Owner` and `AccessControlList`.
- Nested `AccessControlList` stores ordered `Grant` objects.
- Nested `Grant` combines a `Grantee` and permission string.
- Nested `Grantee` serializes `DisplayName`, `ID`, `xsi:type`, and `xmlns:xsi`, defaulting to `CanonicalUser`.
- Equality and hash code are implemented on grant and grantee DTOs for tests and comparisons.

## Control flow
The class is passive. JAX-RS/JAXB reads and writes XML directly from the annotated fields. `S3Acl` consumes and produces these DTOs for ACL conversion.

## State and persistence behavior
No persistence occurs in this model. It represents wire-format ACL state that other handlers apply to Ozone ACL storage.

## Dependencies and integration points
Used by ACL endpoint handlers, `S3Acl`, and XML marshalling with the package-level S3 namespace. Depends on `S3Owner` and `S3Consts.S3_XML_NAMESPACE`.

## Risks and edge cases
Null `aclList`, null `grantee`, or invalid permission strings must be handled by callers; this DTO does not validate them. Default `CanonicalUser` XML attributes are important for AWS client compatibility.

## Test signals
Serialization tests should verify namespace, owner fields, default `xsi:type`, grant equality, and round-trip XML consumed by ACL conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3BucketAcl.java -->
