# sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/OzoneRepair.java

Purpose: `OzoneRepair` is the top-level executable for advanced Ozone repair commands.

Important APIs and types: It extends `GenericCli`, implements `ExtensibleParentCommand`, uses `HddsVersionProvider`, and returns `RepairSubcommand.class` from `subcommandType`.

Control flow: `main` instantiates `OzoneRepair` and runs the provided argv. The extensible command framework discovers subcommands implementing `RepairSubcommand`.

State and persistence behavior: This parent command stores no repair state and performs no direct IO.

Dependencies and integration points: It is the command root for service-loaded repair namespaces such as datanode repair and OM/SCM transaction repairs.

Risks and test signals: Direct risks are command discovery and help/version metadata. Tests should verify subcommand loading and top-level invocation behavior.
