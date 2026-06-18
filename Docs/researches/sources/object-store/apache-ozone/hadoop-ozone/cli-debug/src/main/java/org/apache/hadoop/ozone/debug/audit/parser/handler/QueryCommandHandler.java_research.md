# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/handler/QueryCommandHandler.java

Purpose: `QueryCommandHandler` executes a custom SQL query against an audit parser SQLite database.

Important APIs and types: It uses picocli command/parameter/parent annotations, `AuditParser`, `DatabaseHelper.executeCustomQuery`, and catches `SQLException`.

Control flow: `call()` passes the query string and parent database path to `DatabaseHelper`, prints returned rows to stdout, and prints SQL errors to stderr.

State and persistence behavior: The handler normally reads from SQLite but does not enforce read-only SQL, so supplied statements could mutate state if JDBC allows them through `executeQuery` semantics.

Dependencies and integration points: It is a child command under `AuditParser` and exposes the raw database to operator-provided SQL.

Risks: Arbitrary SQL is accepted; validation is limited to JDBC exceptions. The description tells users to enclose the query in double quotes, which is shell-dependent.

Test signals: Expected output is tab-separated result rows or a printed SQL error message.
