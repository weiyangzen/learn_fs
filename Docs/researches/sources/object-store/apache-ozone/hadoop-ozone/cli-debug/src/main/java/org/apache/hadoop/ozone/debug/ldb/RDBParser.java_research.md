# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/RDBParser.java

Purpose: `RDBParser` is the parent command for RocksDB inspection utilities under `ozone debug ldb`.

Important APIs and types: It implements `DebugSubcommand`, registers with `@MetaInfServices`, and declares `DBScanner`, `ListTables`, `ValueSchema`, and `Checkpoint` as subcommands.

Control flow: Picocli parses inherited required `--db` and dispatches to child commands, which access it via `getDbPath`.

State and persistence behavior: It stores the selected DB path in memory only.

Dependencies and integration points: It integrates RocksDB scanning, schema introspection, column-family listing, and checkpoint creation into the debug CLI.

Risks: All child commands require a valid local RocksDB path; no validation occurs at the parent setter.

Test signals: CLI help, inherited `--db` parsing, and child command access to the path.
