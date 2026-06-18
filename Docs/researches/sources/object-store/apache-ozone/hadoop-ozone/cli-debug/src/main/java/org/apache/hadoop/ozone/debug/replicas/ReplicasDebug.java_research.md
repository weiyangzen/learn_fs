# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/ReplicasDebug.java

Purpose: `ReplicasDebug` registers replica-oriented debug commands under `ozone debug replicas`.

Important APIs and types: It implements `DebugSubcommand`, uses `@MetaInfServices`, and declares subcommands `ChunkKeyHandler` and `ReplicasVerify`.

Control flow and state: The parent command has no fields or direct execution path. Picocli routes to child commands.

Dependencies and integration points: It integrates live-cluster replica diagnostics into the generic Ozone debug command framework.

Risks and test signals: Command registration and help output are the main direct behaviors to test. Operational risks live in the child commands.
