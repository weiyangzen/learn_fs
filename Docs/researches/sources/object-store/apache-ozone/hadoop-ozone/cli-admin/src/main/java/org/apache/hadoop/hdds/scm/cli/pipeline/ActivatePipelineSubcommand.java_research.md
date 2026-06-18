# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/ActivatePipelineSubcommand.java

## Purpose
Implements `ozone admin pipeline activate`, activating a specific pipeline through SCM.

## Important APIs, Types, And Functions
The command extends `ScmSubcommand`, accepts a pipeline ID parameter, builds `HddsProtos.PipelineID`, and calls `ScmClient.activatePipeline`.

## Control Flow
The base class opens the SCM client; `execute` sends one activation RPC.

## State And Persistence
It mutates SCM pipeline lifecycle state.

## Dependencies And Integration Points
Depends on SCM pipeline APIs and protobuf `PipelineID`.

## Risks And Test Signals
No local UUID validation or success message exists. Tests should cover valid/invalid pipeline IDs, already active/closed states, permission failures, and RPC propagation.
