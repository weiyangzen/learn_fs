## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/FreonSubcommand.java

Purpose: marker interface for commands registered under `ozone freon`.

Important APIs/types/functions: empty interface `FreonSubcommand`.

Control flow: `Freon.subcommandType()` returns this marker; classes annotated with `@MetaInfServices(FreonSubcommand.class)` are discoverable as extensible subcommands.

State and persistence behavior: no state.

Dependencies and integration points: used by Freon command classes and metainf-services annotation processor configured in `freon/pom.xml`.

Risks: subcommands missing the marker or service annotation will not be discovered; no compile-time method contract beyond marker identity.

Test signals: service loader/picocli discovery should include all annotated subcommands.
