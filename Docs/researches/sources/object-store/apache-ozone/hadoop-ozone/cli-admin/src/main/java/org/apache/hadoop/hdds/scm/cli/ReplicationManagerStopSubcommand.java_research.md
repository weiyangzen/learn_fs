# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ReplicationManagerStopSubcommand.java

Purpose: This subcommand requests SCM to stop the replication manager.

Important APIs and types: It extends `ScmSubcommand`, is picocli command `stop`, and calls `ScmClient.stopReplicationManager`.

Control flow: `execute` delegates to SCM, prints `Stopping ReplicationManager...`, then prints a second line explaining that SCM was requested to stop it and the stop may take time.

State and persistence behavior: No local persistence. The remote SCM replication-manager service state may transition asynchronously.

Dependencies and integration points: Registered under `ReplicationManagerCommands` and transported through an `ScmClient` implementation.

Risks: It does not poll until stopped. The user-facing text contains `sometime`, and the command assumes the RPC request was accepted if no exception is thrown.

Test signals: Client stop method invocation and the two stdout lines.
