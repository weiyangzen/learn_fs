# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/audit/AuditLogTestUtils.java

Purpose: Static test helper for enabling, reading, verifying, truncating, and deleting Ozone audit logs.

Important APIs/types/functions: `enableAuditLog`, `verifyAuditLog`, `auditLogContains`, `truncateAuditLogFile`, `deleteAuditLogFile`, `AuditAction`, and `AuditEventStatus`.

Control flow: `enableAuditLog` sets the Log4j configuration system property. `verifyAuditLog` waits until `audit.log` contains an action/status pair. `auditLogContains` reads the whole file and checks all requested substrings, returning false on I/O failure. Truncate/delete helpers mutate the fixed audit log path.

State and persistence behavior: Operates on the process system property and a working-directory `audit.log` file.

Dependencies and integration points: Uses Apache Commons IO, Java NIO files, `GenericTestUtils.waitFor`, and the audit logging API.

Risks: Fixed relative file name can collide across tests running in the same directory. Whole-file reads are acceptable for tests but not scalable. Silent false on I/O errors can hide setup problems until timeout.

Test signals: Supports audit integration tests by polling asynchronous log writes and resetting audit log state.
