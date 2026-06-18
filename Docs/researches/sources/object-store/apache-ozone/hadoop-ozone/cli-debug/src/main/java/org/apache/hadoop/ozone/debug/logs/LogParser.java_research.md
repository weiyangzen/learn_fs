# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/LogParser.java

Purpose: `LogParser` is the parent debug command for log parsing and analysis.

Important APIs and types: It implements `DebugSubcommand`, registers with `@MetaInfServices`, and exposes `ContainerLogController`.

Control flow: Picocli routes `ozone debug log container ...` through this parent. The class itself has no executable methods.

State and persistence behavior: No state is stored in this parent.

Dependencies and integration points: It integrates container log analysis commands into the debug CLI.

Risks: The description notes logs must be extracted first; validation happens in subcommands, not here.

Test signals: CLI discovery and help output for the `log` command.
