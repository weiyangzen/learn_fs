<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3Acl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3Acl.java

## Purpose
Conversion utility between S3 ACL grants and Ozone native ACLs for bucket/object ACL compatibility.

## Important APIs, types, and functions
- Defines S3 grant header names and unsupported canned ACL header.
- `ACLType` models S3 permissions: READ, WRITE, READ_ACP, WRITE_ACP, FULL_CONTROL.
- `ACLIdentityType` maps grantee identity types and currently supports only `CanonicalUser`.
- `ozoneNativeAclToS3Acl` converts Ozone user ACLs to S3 `Grant` values.
- `s3AclToOzoneNativeAcl` converts S3 bucket ACL XML grants into volume and bucket Ozone ACL lists.
- `getOzoneAclOnBucketFromS3Permission` and `getOzoneAclOnVolumeFromS3Permission` implement permission expansion.

## Control flow
Read conversion ignores non-user Ozone ACLs, maps broad ACL sets to the best S3 permission, and logs when no S3 mapping is available. Write conversion iterates grants, validates supported grantee type and permission, creates least-privilege volume ACLs, and creates both default and access bucket ACLs.

## State and persistence behavior
This utility itself is stateless. The produced Ozone ACL lists are later persisted by bucket/object ACL handlers through Ozone APIs.

## Dependencies and integration points
Integrated by ACL handlers and `S3BucketAcl` DTOs. Depends on `OzoneAcl`, `IAccessAuthorizer.ACLType`, S3 error translation, and S3 XML grant objects.

## Risks and edge cases
Only canonical users are supported; S3 groups and email grantees return `NotImplemented`. Mapping Ozone ACL sets back to S3 is lossy and priority based, so mixed ACLs may be logged without a precise S3 equivalent. ACL grant header parsing is not in this class.

## Test signals
ACL tests should assert canonical-user conversions, unsupported grantee failures, invalid permission errors, volume least-privilege mappings, and bucket access/default ACL expansion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3Acl.java -->
