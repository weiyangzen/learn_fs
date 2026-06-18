# sources/object-store/apache-ozone/hadoop-hdds/cli-common/src/main/java/org/apache/hadoop/hdds/cli/RepairSubcommand.java

Purpose: Marker interface for subcommands discoverable under `OzoneRepair`.

Important APIs/types/functions: Declares no methods; it is a `ServiceLoader` marker.

Control flow: A repair parent command can return this marker from `subcommandType()`, letting `ExtensibleParentCommand.addSubcommands` discover, sort, and register repair subcommands.

State and persistence behavior: No state; provider metadata controls persistence of discovery.

Dependencies and integration points: Used with picocli and service-loader based CLI extension.

Risks: Same marker-interface risks as admin/debug markers: missing provider registration or missing command annotation prevents loading.

Test signals: Repair CLI help and service discovery tests should confirm registered repair commands appear.
