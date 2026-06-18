# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/ListPipelinesSubcommand.java

## Purpose
Implements `ozone admin pipeline list`, listing pipelines with optional state and replication filters in text or JSON.

## Important APIs, Types, And Functions
Uses `FilterPipelineOptions`, `--state` plus deprecated aliases, hidden `-fst`, and `--json`. It calls `ScmClient.listPipelines`, filters with Java streams, and serializes JSON through `JsonUtils`.

## Control Flow
The command creates a stream from all pipelines, applies replication predicate when present, applies state string filter when present, then either collects to a list for JSON output or prints each pipeline's `toString`.

## State And Persistence
Read-only against SCM pipeline metadata.

## Dependencies And Integration Points
Depends on SCM pipeline list API, `FilterPipelineOptions`, Guava `Strings`, `Pipeline`, and `JsonUtils`.

## Risks And Test Signals
State filtering is free-form string comparison, so typos silently produce empty output. Tests should cover replication filters, deprecated state alias, JSON output, empty list, and mixed case states.
