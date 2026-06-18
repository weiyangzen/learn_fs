# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/common/DatabaseHelper.java

Purpose: `DatabaseHelper` owns SQLite setup, audit log parsing, batch inserts, and query execution for the audit parser.

Important APIs and types: It uses JDBC `DriverManager`, `Connection`, `PreparedStatement`, `ResultSet`, `Properties`, `ParserConsts`, Apache `StringUtils`, and `AuditEntry`.

Control flow: Static initialization loads `commands.properties`. `setup` creates the audit table then calls `insertAudits`. Log parsing reads UTF-8 lines, treats date-prefixed lines as new audit records, appends non-date lines as exception text, splits pipe-delimited fields, builds `AuditEntry` objects, and inserts them in batches of 1000. Query and template methods delegate to `executeStatement`.

State and persistence behavior: It creates and mutates a SQLite database at the provided path. Static `properties` is process-global configuration loaded from resources.

Dependencies and integration points: It is called by load, query, and template handlers and depends on resource SQL keys such as `createAuditTable`, `insertAuditEntry`, and template names.

Risks: `appendException` on an `AuditEntry` with null exception can produce `"null\n..."`. Parsing assumes fixed pipe fields and operation formatting, so malformed audit lines can fail. Custom query execution accepts arbitrary SQL despite help saying read-only.

Test signals: Database file creation, row insertion counts, duplicate handling via SQL uniqueness, template validation, tab-separated query output, and proper handling of multiline exceptions.
