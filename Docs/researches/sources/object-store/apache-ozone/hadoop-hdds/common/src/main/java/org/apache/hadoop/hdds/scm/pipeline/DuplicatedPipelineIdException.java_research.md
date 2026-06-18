# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/DuplicatedPipelineIdException.java

## Purpose
Specific SCM exception indicating a duplicate pipeline ID was detected.

## Important APIs, Types, And Functions
Constructor accepts a message and passes `SCMException.ResultCodes.DUPLICATED_PIPELINE_ID`.

## Control Flow
Thrown by pipeline creation/load paths when a pipeline ID collision is found.

## State And Persistence
Only inherited exception state.

## Dependencies And Integration Points
Depends on `SCMException`. Integrated by pipeline manager and client error handling.

## Risks And Test Signals
Tests should cover duplicate pipeline detection and result-code propagation over RPC.
