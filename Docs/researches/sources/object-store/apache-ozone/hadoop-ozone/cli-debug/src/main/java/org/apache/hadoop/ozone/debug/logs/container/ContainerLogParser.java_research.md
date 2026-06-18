# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/ContainerLogParser.java

Purpose: `ContainerLogParser` parses extracted container logs into a SQLite database used by the container log analysis commands.

Important APIs and types: It extends `AbstractSubcommand`, uses `ContainerLogController`, `ContainerDatanodeDatabase`, `ContainerLogFileParser`, `SQLDBConstants`, `Path`, `Files`, and picocli options `--path` and `--thread-count`.

Control flow: The command normalizes invalid non-positive thread counts to default 10, validates that `--path` is an existing directory, selects an explicit or default database path, validates parent directory existence, creates the raw log table, asks `ContainerLogFileParser` to process entries concurrently, populates the latest container log table, creates indexes, and prints success.

State and persistence behavior: It creates or updates a SQLite database, inserts parsed datanode/container transitions, derives latest container state rows, and creates indexes.

Dependencies and integration points: It is the ingestion entry point for all later `info`, `list`, and duplicate-open queries.

Risks: Invalid path or DB parent errors print and return normally rather than setting non-zero status. Parsing correctness is delegated to utility classes and log format patterns.

Test signals: Created DB tables/indexes, successful parse message, fallback default DB path, and invalid path/thread-count messages.
