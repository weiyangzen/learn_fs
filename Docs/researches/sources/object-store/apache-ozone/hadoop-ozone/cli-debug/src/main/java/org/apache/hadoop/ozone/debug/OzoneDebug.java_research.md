# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/OzoneDebug.java

Purpose: `OzoneDebug` is the top-level `ozone debug` shell entry point.

Important APIs and types: It extends `Shell`, implements `ExtensibleParentCommand`, uses `HddsVersionProvider`, and declares `DebugSubcommand` as the service-loaded subcommand type.

Control flow: `main` creates an instance and delegates to `run(argv)`. `subcommandType()` tells the parent command loader to discover implementations of `DebugSubcommand`.

State and persistence behavior: There is no persistent state. Runtime state is picocli command parsing and service discovery.

Dependencies and integration points: It is the integration point for all debug subcommands registered with `@MetaInfServices(DebugSubcommand.class)`, including native checks, ldb, audit parser, datanode, Kerberos, and log commands.

Risks: Subcommand discovery depends on generated service metadata and classpath correctness. The command name includes a space (`ozone debug`) plus alias `debug`, so launcher wiring must preserve intended invocation style.

Test signals: Successful help/version output and discovery of debug subcommands are the main signals.
