<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/TestOzoneAdmins.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/TestOzoneAdmins.java

Purpose: tests S3/Ozone administrator extraction and authorization matching from `OzoneConfiguration`.

Important APIs/types/functions: `OzoneAdmins`, `getS3AdminsFromConfig`, `getS3AdminsGroupsFromConfig`, `getS3Admins`, `isAdmin`, `isS3Admin`, `OzoneConfigKeys.OZONE_S3_ADMINISTRATORS`, `OZONE_ADMINISTRATORS`, group key variants, and `UserGroupInformation.createUserForTesting`.

Control flow: each parameterized case sets admin or admin-group configuration keys, constructs an `OzoneAdmins` view, then checks direct user and group-based authorization. Tests also cover behavior when configuration contains or omits explicit S3 admins and the static `isS3Admin` helper is given null UGI.

State and persistence behavior: configuration is in-memory per test. No disk or external service state is used.

Dependencies and integration points: integrates Ozone config keys, Hadoop UGI group membership, and the `OzoneAdmins` policy utility.

Risks: authorization behavior depends on fallback rules between S3-specific and Ozone-wide admin keys. Misinterpreting empty/unset admin config can create over-permissive or under-permissive access.

Test signals: asserts extracted admin users/groups, direct user admin checks, group-only admin checks, behavior with admin config enabled/disabled, static S3 admin decisions, and null-user denial.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/TestOzoneAdmins.java -->
