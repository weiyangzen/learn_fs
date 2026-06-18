# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/CreatePipelineSubcommand.java

## Purpose
Implements `ozone admin pipeline create`, creating a replication pipeline.

## Important APIs, Types, And Functions
Options include replication type (hidden/deprecated full name aliases) and replication factor. `execute` rejects CHAINED, EC, and STAND_ALONE, then calls `ScmClient.createReplicationPipeline(type, factor, NodePool.getDefaultInstance())`.

## Control Flow
After validation, SCM creates a RATIS pipeline and the command prints the created ID and full pipeline string when non-null.

## State And Persistence
It mutates SCM pipeline metadata by allocating a new pipeline.

## Dependencies And Integration Points
Depends on `HddsProtos.ReplicationType`, `ReplicationFactor`, `NodePool`, and SCM pipeline allocation.

## Risks And Test Signals
The description says replication type is RATIS while still accepting a hidden type option. Tests should cover unsupported types, factor values, null return, creation failure, and output format.
