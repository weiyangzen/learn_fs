# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ReplicationManagerCommands.java

Purpose: This class registers the `ozone admin replicationmanager` command group for starting, stopping, and checking SCM's replication manager.

Important APIs and types: It implements `AdminSubcommand`, is annotated with picocli `@Command`, uses `HddsVersionProvider`, registers subcommands `ReplicationManagerStartSubcommand`, `ReplicationManagerStopSubcommand`, and `ReplicationManagerStatusSubcommand`, and uses `@MetaInfServices(AdminSubcommand.class)` for discovery.

Control flow: It has no executable methods. Picocli and service-provider loading use the annotations to expose the command group.

State and persistence behavior: No local state or persistence.

Dependencies and integration points: It integrates admin CLI discovery with SCM replication-manager control subcommands.

Risks: Command name or service registration changes can break admin CLI compatibility. Help text is minimal and relies on child commands for details.

Test signals: CLI discovery of `replicationmanager` and routing of `start`, `stop`, and `status` subcommands.
