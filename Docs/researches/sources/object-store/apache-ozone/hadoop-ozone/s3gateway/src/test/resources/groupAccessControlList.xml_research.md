# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/resources/groupAccessControlList.xml

## Purpose
XML fixture for S3 ACL parsing tests that include a mix of canonical user, group, email, and owner grants.

## Important APIs, types, and functions
The document uses the S3 `AccessControlPolicy` schema namespace, with `Owner`, `AccessControlList`, `Grant`, `Grantee`, and `Permission` elements. Grantee `xsi:type` values include `CanonicalUser`, `Group`, and `AmazonCustomerByEmail`.

## Control flow
Consumers parse owner metadata, then process five grants: owner full control, AllUsers read, LogDelivery write, AmazonCustomerByEmail write ACL, and another canonical user read ACL.

## State and persistence behavior
It is static test data, not persisted application state. It represents serialized ACL state as it would arrive over S3-compatible XML APIs.

## Dependencies and integration points
The fixture integrates S3 gateway XML binding/parsing with ACL conversion logic and namespace handling, including nested elements that reset XML namespace to empty.

## Risks and edge cases
Mixed grantee types and namespace overrides are the main edge cases. Email grantees may be unsupported by Ozone logic, so tests using this fixture likely assert rejection or partial interpretation.

## Test signals
Useful signals are parsed grant count, grantee type recognition, owner canonical id/display name, and permission mapping for group and user ACLs.
