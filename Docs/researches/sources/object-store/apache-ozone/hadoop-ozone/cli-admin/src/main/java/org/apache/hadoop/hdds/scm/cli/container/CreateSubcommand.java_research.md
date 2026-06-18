# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/CreateSubcommand.java

## Purpose
Implements `ozone admin container create`, creating a new container through SCM with optional replication settings.

## Important APIs, Types, And Functions
Options include `--owner` and `ShellReplicationOptions`. `execute` derives `ReplicationConfig` from command params or configuration, defaults to `STAND_ALONE`/`ONE` when absent, and calls `ScmClient.createContainer(replicationConfig, owner)`.

## Control Flow
The command parses replication configuration, falls back to the legacy default, sends the create RPC, and prints the new container ID and replication config.

## State And Persistence
It mutates SCM state by allocating container metadata and a pipeline. Local state is transient.

## Dependencies And Integration Points
Depends on `ShellReplicationOptions`, `ReplicationConfig`, `HddsProtos`, `ContainerWithPipeline`, and SCM allocation APIs.

## Risks And Test Signals
It constructs a new `OzoneConfiguration` instead of reusing the command's loaded configuration, which may miss CLI/config context. Tests should cover default replication, Ratis/EC parsing, owner propagation, and allocation failure handling.
