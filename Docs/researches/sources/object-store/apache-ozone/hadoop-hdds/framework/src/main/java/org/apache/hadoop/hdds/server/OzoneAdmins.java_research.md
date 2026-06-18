# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/OzoneAdmins.java

## Purpose

`OzoneAdmins` models configured Ozone administrator users and groups and provides authorization helpers for superuser, read-only admin, and S3 admin checks.

## Important APIs, Types, and Functions

Constructors create immutable username/group sets. Static factories read standard Ozone config keys for admins, read-only admins, and S3 admins. `isAdmin(UserGroupInformation)` checks wildcard, short username membership, and group intersection. `checkAdminUserPrivilege` throws `AccessControlException` when a non-admin attempts an admin operation. S3 helpers provide fallback from S3-specific config to general admin config and include the current service user.

## Control Flow

Callers build an instance from configuration and call `isAdmin` or `checkAdminUserPrivilege` during authorization. Setter `setAdminUsernames` can refresh the volatile username set while groups remain constructor-defined.

## State and Persistence Behavior

State is in-memory only: volatile admin usernames and immutable admin groups. Persistent source is `OzoneConfiguration`.

## Dependencies and Integration Points

It integrates Ozone config keys, Hadoop UGI, Hadoop `StringUtils`, Guava `Sets.intersection`, and access-control exception handling in server-side authorization.

## Risks and Edge Cases

The starter/current user is automatically added in several paths, which is intentional but security-sensitive. Group updates require a new object because only usernames have a setter in common usage. `getS3Admins` suppresses IOException by returning an empty user set before group evaluation.

## Test Signals

Test wildcard admin, short-name matching, group matching, starter user insertion, read-only config parsing, S3 fallback behavior, IOException fallback, setter refresh, and access exception messages.
