# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/ContainerLogController.java

Purpose: `ContainerLogController` groups container log parse/query commands and manages the inherited SQLite database path.

Important APIs and types: It extends `AbstractSubcommand`, uses picocli inherited `--db`, `Path`, `Files`, `Paths`, and `SQLDBConstants.DEFAULT_DB_FILENAME`.

Control flow: Subcommands are `info`, `parse`, `duplicate-open`, and `list`. `resolveDbPath()` uses a provided `--db` when present, validating parent directory existence, or falls back to `container_datanode.db` in the current directory if it exists.

State and persistence behavior: The controller stores the db path parameter. It does not create or mutate the DB; parse/query subcommands do that.

Dependencies and integration points: It is the common parent for all container log operations and centralizes default DB behavior.

Risks: When no `--db` is provided and no default file exists, query commands throw `IllegalArgumentException`. Provided paths are not required to already exist, allowing parse to create them.

Test signals: Correct default DB discovery message, exception for missing default DB, and parent-directory validation for explicit paths.
