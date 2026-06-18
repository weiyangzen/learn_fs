# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/om/OMDebug.java

Purpose: `OMDebug` is the service-provider entry point for OM-related `ozone debug` subcommands.

Important APIs and types: It implements `DebugSubcommand`, is annotated with `@MetaInfServices`, and declares picocli subcommands `CompactionLogDagPrinter`, `PrefixParser`, and `ContainerToKeyMapping`. It exposes inherited `--db` through `getDbPath`.

Control flow: Picocli instantiates this parent command, parses the required `--db` option with inherited scope, and subcommands read the configured path from `parent.getDbPath()`.

State and persistence behavior: It stores only the CLI-provided OM RocksDB path. It performs no direct IO.

Dependencies and integration points: The class is discovered by the extensible debug command framework and groups offline OM DB tools.

Risks and test signals: Missing or invalid `--db` handling is delegated to subcommands. Tests should confirm command registration, inherited option parsing, and that each child sees the same DB path.
