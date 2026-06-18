# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/AdminSubcommand.java

Purpose: Marker interface for subcommands discoverable under `OzoneAdmin`.

Important APIs/types/functions: Declares no methods. Implementing classes use it as their service-loader type.

Control flow: `ExtensibleParentCommand.addSubcommands` can load providers of this interface, inspect their picocli command annotation, sort them by command name, and add them to an admin parent command.

State and persistence behavior: No state. Persistent behavior comes from `META-INF/services` provider files generated or supplied by implementations.

Dependencies and integration points: Integrated with `ExtensibleParentCommand`, `ServiceLoader`, picocli annotations, and admin CLI modules.

Risks: Implementations must be annotated with `@CommandLine.Command` and registered as services; otherwise dynamic loading will fail or throw a null annotation issue.

Test signals: Service-loader tests for admin plugins should verify that implementations appear under the admin command.
