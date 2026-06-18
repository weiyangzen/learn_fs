# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/ExtensibleParentCommand.java

Purpose: Defines the dynamic subcommand extension contract for Ozone CLI parent commands.

Important APIs/types/functions: `subcommandType()` returns the marker interface class used for service discovery. Static `addSubcommands(CommandLine)` recursively registers discovered subcommands.

Control flow: For any command object implementing this interface, the loader calls `ServiceLoader.load` with its marker type, creates `CommandLine` wrappers using the parent's factory, sorts providers by their `@CommandLine.Command.name()`, and adds them to the parent. It then recurses into all subcommands.

State and persistence behavior: No internal state. Persistent discovery depends on service provider metadata in jars.

Dependencies and integration points: Works with `AdminSubcommand`, `DebugSubcommand`, `RepairSubcommand`, picocli, `ServiceLoader`, and `MetaInfServices` generated metadata.

Risks: It assumes every provider class has a `@CommandLine.Command` annotation; if absent, dereferencing `commandAnnotation.name()` fails. Duplicate names overwrite in the sorted map before registration. Service loading happens at CLI construction, so classpath problems affect startup.

Test signals: Tests should include deterministic ordering, recursive registration, duplicate-name handling expectations, and provider classes missing annotations.
