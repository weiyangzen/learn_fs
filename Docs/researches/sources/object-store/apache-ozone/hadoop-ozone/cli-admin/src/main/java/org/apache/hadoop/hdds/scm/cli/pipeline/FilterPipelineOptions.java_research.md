# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/FilterPipelineOptions.java

## Purpose
Provides reusable pipeline replication filters for list and close commands.

## Important APIs, Types, And Functions
Options include `--type`, `--replication`, deprecated `--filterByFactor/--filter-by-factor`, and hidden deprecated `-ffc`. `getReplicationFilter` returns an optional `Predicate<Pipeline>` based on exact `ReplicationConfig` or replication type string.

## Control Flow
Factor and replication are mutually exclusive. Replication requires replication type and is parsed with `ReplicationConfig.parse`. Type-only mode compares pipeline replication type case-insensitively. With no filter options, it returns `Optional.empty()`.

## State And Persistence
Holds only parsed invocation options.

## Dependencies And Integration Points
Used by `ListPipelinesSubcommand` and `ClosePipelineSubcommand`. Depends on Ozone replication config classes and `Pipeline.getReplicationConfig`.

## Risks And Test Signals
Invalid type names throw `IllegalArgumentException`. Type comparison uses string names rather than enum parsing. Tests should cover factor alias, EC replication string parsing, missing type with replication, mutually exclusive options, and case-insensitive type filtering.
