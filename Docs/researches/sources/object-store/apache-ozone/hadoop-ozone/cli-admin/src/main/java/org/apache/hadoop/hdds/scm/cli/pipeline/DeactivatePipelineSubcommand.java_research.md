# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/DeactivatePipelineSubcommand.java

## Purpose
Implements `ozone admin pipeline deactivate`, deactivating a specific pipeline through SCM.

## Important APIs, Types, And Functions
The command accepts a pipeline ID parameter, builds `HddsProtos.PipelineID`, and calls `ScmClient.deactivatePipeline`.

## Control Flow
`ScmSubcommand` handles client lifecycle; `execute` performs one deactivate RPC.

## State And Persistence
It mutates SCM pipeline lifecycle state.

## Dependencies And Integration Points
Depends on SCM pipeline APIs and protobuf IDs.

## Risks And Test Signals
No local ID validation or success output. Tests should cover valid/invalid pipeline IDs, already inactive/closed behavior, and permission/RPC failures.
