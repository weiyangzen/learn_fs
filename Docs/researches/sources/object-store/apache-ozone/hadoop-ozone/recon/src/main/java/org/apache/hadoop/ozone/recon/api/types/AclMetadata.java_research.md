<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/AclMetadata.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/AclMetadata.java

## Purpose

`AclMetadata` is a JSON DTO representing a single Ozone ACL in Recon API responses.

## Important APIs and Types

Fields are `type`, `name`, `scope`, and `aclList`, exposed through Jackson `@JsonProperty`. A builder enforces non-null type, name, and scope. Static helpers convert one or many `OzoneAcl` instances.

## Control Flow

`fromOzoneAcl` returns null for null input; otherwise it uppercases ACL type and scope strings, copies the ACL name, copies ACL rights strings, and builds the DTO. `fromOzoneAcls` streams a list through that converter.

## State and Persistence

The DTO is immutable after builder construction in normal use, though fields are not declared final. It persists nothing.

## Dependencies and Integration Points

It is used by object metadata DTOs such as `BucketObjectDBInfo` and likely volume/key metadata wrappers to serialize ACLs.

## Risks and Edge Cases

`fromOzoneAcls` does not null-check the list and will include null entries if the input contains null ACLs. The builder does not require `aclList`, so responses may contain null ACL lists.

## Test Signals

Tests should cover conversion from user/group ACLs, null ACL input, null ACL list handling, uppercase type/scope, and builder non-null enforcement.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/AclMetadata.java -->
