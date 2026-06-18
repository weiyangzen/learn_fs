# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/resources/userAccessControlList.xml

## Purpose
XML fixture for S3 ACL parsing tests focused on canonical-user grants.

## Important APIs, types, and functions
The file is an S3 `AccessControlPolicy` document with an `Owner` and two `Grant` entries. Both grantees are `CanonicalUser`; permissions are `FULL_CONTROL` for the owner and `READ_ACP` for a second account.

## Control flow
Consumers parse the owner first, then iterate the ACL grants and map canonical IDs to Ozone/S3 ACL entries. The first owner ID intentionally spans whitespace/newline content inside the `ID` element.

## State and persistence behavior
Static serialized test state only. It models request/response XML used by S3 ACL APIs.

## Dependencies and integration points
This fixture exercises XML namespace handling, canonical user parsing, and permission translation in the S3 gateway.

## Risks and edge cases
Whitespace around canonical IDs can expose parsers that fail to trim or normalize element text. It does not include groups, emails, invalid permissions, or malformed XML.

## Test signals
Expected signals are correct owner extraction, two recognized grants, canonical-user grantee handling, and `FULL_CONTROL`/`READ_ACP` permission mapping.
