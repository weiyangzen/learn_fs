# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/audit/TestOzoneAuditLogger.java

Purpose: Tests formatting, severity routing, filtering, and exception logging for `AuditLogger`.

Important APIs/types/functions: `AuditLogger`, `AuditLoggerType.OMLOGGER`, `AuditMessage.Builder`, `logWriteSuccess`, `logWriteFailure`, `logReadSuccess`, `logReadFailure`, `logAuthFailure`, `refreshDebugCmdSet`, `AuditLogger.AUDIT_LOG_DEBUG_CMD_LIST_PREFIX`, and `AuditMessage.getFormattedMessage`.

Control flow: Static setup selects `auditlog.properties` and builds reusable audit messages. Each test logs a message, reads `audit.log`, retries for asynchronous delivery, and checks expected level/logger/class/message substrings. The exclusion test configures a debug command list to suppress `CREATE_VOLUME`. A multiline exception test asserts both formatted audit line and stack trace lines.

State and persistence behavior: Writes and clears a working-directory `audit.log`; deletes it after all tests. `AUDIT.refreshDebugCmdSet` updates logger filtering from configuration.

Dependencies and integration points: Integrates Log4j2 config, Ozone configuration, commons-io file reads/writes, dummy audit action/entity, and AssertJ.

Risks: File-based assertions can be flaky under parallel execution or if another test writes `audit.log`. Line-index assumptions in multiline exception checks couple to logger layout.

Test signals: Good signal for audit log level policy, message content, debug exclusion filtering, auth failure logging, and exception stack trace inclusion.
