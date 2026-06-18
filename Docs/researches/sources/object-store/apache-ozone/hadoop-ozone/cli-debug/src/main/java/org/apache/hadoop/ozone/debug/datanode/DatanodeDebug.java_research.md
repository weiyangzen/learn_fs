# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/DatanodeDebug.java

Purpose: `DatanodeDebug` is the parent command for datanode-specific debug operations.

Important APIs and types: It implements `DebugSubcommand`, registers with `@MetaInfServices`, and declares `ContainerCommands` as its subcommand.

Control flow: Picocli dispatches `ozone debug datanode container ...` commands through this parent. The class itself contains no methods.

State and persistence behavior: No state is stored or persisted.

Dependencies and integration points: It integrates datanode local container inspection/export commands into the extensible debug CLI.

Risks: Service registration and subcommand class availability are required for discovery.

Test signals: CLI help/discovery showing `datanode` and `container` subcommands.
