# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ReplicationManagerStatusSubcommand.java

Purpose: This subcommand reports whether SCM's replication manager is running.

Important APIs and types: It extends `ScmSubcommand`, is picocli command `status`, and calls `ScmClient.getReplicationManagerStatus`.

Control flow: `execute` reads the boolean status from SCM and prints either `ReplicationManager is Running.` or `ReplicationManager is Not Running.`.

State and persistence behavior: Read-only command; no local state or persistence.

Dependencies and integration points: Registered under the replication manager command group and depends on SCM's status RPC.

Risks: It provides only a boolean summary, not queue depth, health, or last-run details. IOException propagates.

Test signals: Correct output for true and false client responses.
