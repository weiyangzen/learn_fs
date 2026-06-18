# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/Vapor.java

Purpose: command root for `ozone vapor`, a Freon-derived load generator that uses Ozone server components.

Important APIs/types/functions: class `Vapor extends Freon`, `subcommandType`, and `main`. The `@Command` annotation configures picocli name, help, version provider, and description.

Control flow: `main` constructs `Vapor` and delegates to `Freon.run(args)`. `subcommandType` returns `VaporSubcommand.class`, allowing Freon to discover/register only subcommands that implement this marker.

State/persistence: no state beyond inherited Freon command state and Ozone configuration handling.

Dependencies/integration: picocli, `HddsVersionProvider`, `Freon`, and Java service registration via marker subcommands such as `SCMThroughputBenchmark`, `StreamingGenerator`, and container generators.

Risks: because command discovery is marker-interface based, missing `@MetaInfServices(VaporSubcommand.class)` or wrong marker implementation in a subcommand makes it invisible under `ozone vapor`.

Test signals: no local test in this subset. A command-discovery smoke test should verify expected Vapor subcommands appear.
