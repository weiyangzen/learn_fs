# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/handler/LoadCommandHandler.java

Purpose: `LoadCommandHandler` implements `ozone debug auditparser <db> load <logs>`.

Important APIs and types: It implements `Callable<Void>`, uses picocli `@Command`, `@Parameters`, `@ParentCommand`, `AuditParser`, `DatabaseHelper`, and `HddsVersionProvider`.

Control flow: Picocli captures one log file path and parent database path. `call()` invokes `DatabaseHelper.setup(database, logs)` and prints success or failure text.

State and persistence behavior: It can create and populate a SQLite database via `DatabaseHelper`. The handler itself stores only parsed command parameters.

Dependencies and integration points: It is a child command of `AuditParser` and depends on `DatabaseHelper` for table creation, parsing, and insert behavior.

Risks: The parameter description says "file(s)" but the implementation accepts a single string and `DatabaseHelper` reads one path. Exceptions from setup propagate instead of being converted to user-friendly CLI failures.

Test signals: Successful load message and resulting rows in the SQLite audit table.
