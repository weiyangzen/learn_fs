# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/handler/TemplateCommandHandler.java

Purpose: `TemplateCommandHandler` executes named predefined audit queries.

Important APIs and types: It uses picocli annotations, `AuditParser`, `DatabaseHelper.validateTemplate`, `DatabaseHelper.executeTemplate`, and catches `SQLException`.

Control flow: `call()` validates the supplied template name against loaded SQL properties. Valid templates execute and print rows; invalid names print an error to stderr.

State and persistence behavior: The command reads from the SQLite audit DB and does not directly persist state.

Dependencies and integration points: It exposes templates documented in the command description, including top users, commands, and active times, backed by entries in `commands.properties`.

Risks: Template availability and help text can drift because available names are hard-coded in the description but validated dynamically from properties.

Test signals: Valid template output, invalid template error text, and SQL exception text on query failure.
