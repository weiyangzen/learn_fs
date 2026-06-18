# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/ClosePipelineSubcommand.java

## Purpose
Implements `ozone admin pipeline close`, closing one pipeline or all non-closed pipelines optionally filtered by replication config.

## Important APIs, Types, And Functions
It uses a required arg group containing either pipeline ID or `--all`, plus `FilterPipelineOptions`. Single-ID mode calls `closePipeline`; all mode lists pipelines, filters out CLOSED and optionally applies replication predicate, then closes each.

## Control Flow
If a specific pipeline ID is provided with replication filters, it throws. In `--all`, it builds a list from `scmClient.listPipelines`, prints a count, and attempts to close each, logging per-pipeline IOExceptions without aborting the loop.

## State And Persistence
It mutates SCM pipeline lifecycle state by requesting close transitions.

## Dependencies And Integration Points
Depends on `ScmClient.listPipelines`, `closePipeline`, `FilterPipelineOptions`, Guava `Strings`, and `Pipeline` state/config APIs.

## Risks And Test Signals
Per-pipeline failures in `--all` only print to stderr and do not cause a non-zero exit. Tests should cover arg-group exclusivity, filters with single ID rejection, all-mode filtering, closed pipelines ignored, and partial close failures.
