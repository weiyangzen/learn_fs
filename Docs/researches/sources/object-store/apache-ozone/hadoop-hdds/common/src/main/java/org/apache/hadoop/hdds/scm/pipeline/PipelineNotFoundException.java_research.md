# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineNotFoundException.java

## Purpose
Signals that a requested pipeline is missing from `PipelineManager`.

## Important APIs and types
It extends `SCMException` and always uses `ResultCodes.PIPELINE_NOT_FOUND`. Constructors support a default message-less exception and a message-bearing exception.

## Control flow and state
There is no mutable state beyond the superclass exception fields. The class exists to preserve typed catch sites and consistent SCM result coding.

## Dependencies and integration points
Pipeline manager and SCM client code can throw or catch this type while still using SCM's common result-code taxonomy.

## Risks and test signals
Tests should assert the result code when callers map SCM exceptions to protocol or client errors. Behavior is otherwise trivial.
