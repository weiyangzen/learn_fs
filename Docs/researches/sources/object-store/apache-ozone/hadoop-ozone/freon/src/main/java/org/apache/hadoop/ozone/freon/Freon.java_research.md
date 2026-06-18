## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/Freon.java

Purpose: top-level `ozone freon` CLI command and extensible parent for all Freon subcommands.

Important APIs/types/functions: extends `GenericCli` and implements `ExtensibleParentCommand`. `execute` initializes metrics/tracing and delegates to picocli. `subcommandType` returns `FreonSubcommand`. `startHttpServer` and `stopHttpServer` manage optional internal HTTP server. `main` runs the command. `isInteractive` reports console presence.

Control flow: command execution captures `OzoneConfiguration`, initializes metrics as `ozone-freon`, wraps the full command in a tracing span, then lets `GenericCli` discover and run registered subcommands. Subcommands call `BaseFreonGenerator.init`, which may call `startHttpServer`.

State and persistence behavior: holds configuration, optional `FreonHttpServer`, and an immutable interactive flag. Persistent effects are delegated to subcommands.

Dependencies and integration points: picocli, HDDS CLI framework, metrics, OpenTelemetry tracing, `FreonSubcommand` service discovery.

Risks: HTTP server startup errors are logged but non-fatal; `interactive` is computed once from `System.console`; tracing span name includes raw argv.

Test signals: CLI should discover `@MetaInfServices` subcommands and initialize metrics/tracing before command execution.
