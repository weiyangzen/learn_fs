# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/TestOzoneAcls.java

Purpose: validates parsing and representation of `OzoneAcl` strings for user, group, world, and anonymous identities, including rights bitsets and ACL scope suffixes.

Important APIs/types/functions: covers `OzoneAcl.parseAcl`, `OzoneAcl.parseAcls`, `isSet`, `getAclList`, `getName`, `getType`, and `getAclScope`. It checks rights `READ`, `WRITE`, `DELETE`, `LIST`, `NONE`, `CREATE`, `READ_ACL`, `WRITE_ACL`, and `ALL`.

Control flow and state: `testAclParse` drives a validity matrix of accepted and rejected strings. Later tests inspect parsed ACL objects and comma-separated ACL lists. World and anonymous identities normalize names such as `WORLD` and `ANONYMOUS`; scope strings like `[DEFAULT]` and `[ACCESS]` are decoded into enum values.

Dependencies and integration points: depends on `IAccessAuthorizer` identity and ACL enums and AssertJ/JUnit assertions. These parsing contracts feed OM ACL persistence, authorization checks, and CLI/API ACL input handling.

Risks and test signals: protects against accepting malformed identity prefixes, empty names where not allowed, invalid right characters, and losing scope metadata. Notably some strings containing extra valid rights plus unknown-looking characters are expected to parse only when all characters map to known ACL rights, so rights alphabet changes must be deliberate.
