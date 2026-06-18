# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/AuditParser.java

Purpose: `AuditParser` is the parent command for parsing Ozone audit logs into a SQLite database and querying them.

Important APIs and types: It implements `DebugSubcommand`, registers with `@MetaInfServices`, uses picocli `@Command`, `@Parameters`, `HddsVersionProvider`, and subcommands `LoadCommandHandler`, `TemplateCommandHandler`, and `QueryCommandHandler`.

Control flow: Picocli parses one required database path at the parent level, then dispatches to load/template/query handlers. `getDatabase()` exposes that path to child commands through `@ParentCommand`.

State and persistence behavior: The command itself holds only the parsed database path. SQLite persistence is performed by `DatabaseHelper` in the child command flows.

Dependencies and integration points: It integrates audit parsing into `ozone debug` and defines the table shape in user-facing parameter help.

Risks: The help describes a single `audit` table and uniqueness constraint; implementation correctness depends on external `commands.properties` SQL matching that description.

Test signals: CLI help, database parameter parsing, and successful dispatch to load/query/template handlers.
