<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureCommands.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureCommands.java

Purpose: Root command for dynamic server reconfiguration. It defines common options and registers `start`, `status`, and `properties` subcommands.

Important APIs and types: `AdminSubcommand`, `@MetaInfServices`, `OzoneAdmin`, `ContainerOperationClient`, `ScmClient`, `HddsProtos.NodeType`, `--service`, `--address`, and `--in-service-datanodes`.

Control flow: Picocli parses service/address/batch options. `getService()` converts the service string with `NodeType.valueOf`. `getAllOperableNodesClientRpcAddress()` opens a `ContainerOperationClient`, asks `ReconfigureSubCommandUtil` for IN_SERVICE datanode addresses, wraps IOExceptions in RuntimeException, and closes the client.

State and persistence behavior: Holds parsed CLI options for a command invocation only. No local persistence.

Dependencies and integration points: Registered as an admin subcommand provider. It bridges the generic Ozone admin root configuration to SCM node discovery for datanode batch reconfiguration.

Risks: `NodeType.valueOf` is case-sensitive and can throw for lowercase service values. Batch mode can be selected with a non-DATANODE service, while the base class still executes datanode operations.

Test signals: Command registration, service parsing, address requirement via base class, SCM client closure, batch query failure wrapping, and valid/invalid service strings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureCommands.java -->
