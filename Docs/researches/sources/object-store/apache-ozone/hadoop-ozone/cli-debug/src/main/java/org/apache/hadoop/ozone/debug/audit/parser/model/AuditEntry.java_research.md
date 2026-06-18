# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/model/AuditEntry.java

Purpose: `AuditEntry` is the data model for parsed audit log records before insertion into SQLite.

Important APIs and types: It is a mutable POJO with fields for timestamp, level, logger, user, IP, operation, params, result, and exception, plus a nested fluent `Builder`.

Control flow: Callers either use setters or the builder to populate fields. `setException` trims text, and `appendException` appends a newline and trimmed continuation text to the existing exception string.

State and persistence behavior: Instances hold in-memory parsed state. `DatabaseHelper` maps instances into the persistent SQLite audit table.

Dependencies and integration points: The class is used by the audit parser's log parsing and insert path.

Risks: `appendException` assumes `exception` is already initialized; if it is null, concatenation can persist a `"null"` prefix. The builder does no validation, so malformed/null fields reach SQL binding.

Test signals: Expected signals are correct field extraction, multiline exception preservation, and inserted SQL column values.
