# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/package-info.java

## Purpose
Package documentation for SCM pipeline support. It states that Ozone supports multiple pipeline kinds, such as Ratis and simple/standalone replication, and that pipeline managers live under this package.

## Important APIs and types
No executable APIs are declared. The package contains pipeline entities and managers; in this subset the important behavioral types are `Pipeline`, `PipelineID`, and `PipelineNotFoundException`.

## Control flow, state, and persistence
There is no runtime control flow or state.

## Dependencies and integration points
The package description frames integration between SCM, replication protocols, datanodes, and pipeline managers.

## Risks and test signals
No direct tests are needed for this file. Documentation should be updated if pipeline kinds or package ownership change.
