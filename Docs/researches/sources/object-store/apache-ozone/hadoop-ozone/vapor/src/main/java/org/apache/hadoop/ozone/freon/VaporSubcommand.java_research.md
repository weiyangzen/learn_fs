# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/VaporSubcommand.java

Purpose: marker interface used to identify subcommands belonging to `ozone vapor`.

Important APIs/types/functions: empty interface `VaporSubcommand`.

Control flow: no runtime logic. `Vapor.subcommandType()` returns this interface, and subcommands use `@MetaInfServices(VaporSubcommand.class)` so service discovery can find them.

State/persistence: none.

Dependencies/integration: integrates Freon command loading with the `org.kohsuke.MetaInfServices` service-generation pattern used by Vapor subcommands.

Risks: marker interfaces have no compile-time behavior contract; command classes must separately implement `Callable`/picocli annotations correctly.

Test signals: indirect command-discovery tests are the useful coverage; no direct test needed beyond compilation.
