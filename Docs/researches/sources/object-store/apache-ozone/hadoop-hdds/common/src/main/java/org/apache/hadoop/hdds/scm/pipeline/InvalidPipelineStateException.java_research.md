# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/InvalidPipelineStateException.java

## Purpose
Specific SCM exception indicating a pipeline is in a state invalid for the requested operation.

## Important APIs, Types, And Functions
Constructor accepts a message and maps to `SCMException.ResultCodes.INVALID_PIPELINE_STATE`.

## Control Flow
Thrown by pipeline manager/state-machine operations before illegal transitions or actions.

## State And Persistence
Only inherited exception state.

## Dependencies And Integration Points
Depends on `SCMException`. Integrated by pipeline lifecycle management, allocation, and close/destroy paths.

## Risks And Test Signals
Tests should cover invalid state transitions, user-facing messages, and result-code mapping.
