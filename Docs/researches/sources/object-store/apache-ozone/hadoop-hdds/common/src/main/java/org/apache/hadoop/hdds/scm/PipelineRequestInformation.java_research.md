# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/PipelineRequestInformation.java

## Purpose
Carries request metadata used by pipeline selection, currently just requested size.

## Important APIs, Types, And Functions
`PipelineRequestInformation` is final with `getSize()`. Nested `Builder` has `getBuilder()`, `setSize(long)`, and `build()`.

## Control Flow
Callers build a value and pass it to pipeline-selection logic that may consider requested allocation size.

## State And Persistence
The value is immutable and transient. No serialization is defined in this class.

## Dependencies And Integration Points
Integrates with SCM pipeline choose policies and block/container allocation paths.

## Risks And Test Signals
There is no validation for negative size. Tests should cover policy behavior for zero, positive, and invalid sizes at the consuming layer.
