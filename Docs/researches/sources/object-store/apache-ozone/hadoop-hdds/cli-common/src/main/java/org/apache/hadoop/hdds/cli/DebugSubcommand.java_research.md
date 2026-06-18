# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/DebugSubcommand.java

Purpose: Marker interface for subcommands discoverable under `OzoneDebug`.

Important APIs/types/functions: It has no methods and exists only as a service-loader classification type.

Control flow: Parent commands implementing `ExtensibleParentCommand` can return this marker from `subcommandType()`. The common loader then discovers providers, wraps them in picocli command lines, and registers them recursively.

State and persistence behavior: No state or persistence except service metadata provided by implementations.

Dependencies and integration points: Used by debug-oriented CLI modules with picocli and `ServiceLoader`.

Risks: Missing service registration or missing command annotation on an implementation prevents discovery. Because the interface has no type contract, behavior correctness lives entirely in implementing classes.

Test signals: Dynamic debug CLI registration tests and command help output are the relevant signals.
