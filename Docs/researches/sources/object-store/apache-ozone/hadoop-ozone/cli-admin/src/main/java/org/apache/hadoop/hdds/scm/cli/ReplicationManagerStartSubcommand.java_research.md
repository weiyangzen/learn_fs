# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ReplicationManagerStartSubcommand.java

Purpose: This subcommand asks SCM to start its replication manager.

Important APIs and types: It extends `ScmSubcommand`, is picocli command `start`, and calls `ScmClient.startReplicationManager`.

Control flow: `execute` delegates to the SCM client and then prints `Starting ReplicationManager...`.

State and persistence behavior: No local persistence. Remote SCM replication-manager runtime state may change.

Dependencies and integration points: Registered under `ReplicationManagerCommands` and relies on `ContainerOperationClient` or another `ScmClient` implementation for transport.

Risks: The message is printed after the RPC returns but says starting, not started; actual async semantics are determined by SCM. IOException is not caught and will propagate to the CLI framework.

Test signals: Client method invocation and the expected stdout line.
