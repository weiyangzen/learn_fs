# sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/datanode/DatanodeRepair.java

Purpose: `DatanodeRepair` registers datanode-specific repair commands.

Important APIs and types: It implements `RepairSubcommand`, uses `@MetaInfServices`, and declares `UpgradeContainerSchema` as a picocli subcommand.

Control flow and state: The class has no fields or direct execution method. Picocli routes to `upgrade-container-schema`.

Dependencies and integration points: It plugs datanode repair tooling into `OzoneRepair` service discovery.

Risks and test signals: Command registration and help output are the main direct behaviors. Upgrade behavior is in `UpgradeContainerSchema`.
