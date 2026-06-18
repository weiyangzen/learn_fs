# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/NodeSelectionMixin.java

## Purpose
Provides a standardized mutually exclusive datanode selector mixin for commands that can target a node by UUID, hostname, or IP.

## Important APIs, Types, And Functions
`NodeSelectionMixin` contains an exclusive `Selection` arg group. Public getters return effective node ID with precedence `--node-id` over deprecated hidden `--id` over deprecated hidden `--uuid`, plus hostname and IP values.

## Control Flow
Picocli enforces that at most one selector from the group is present. Commands read getters to filter/query SCM.

## State And Persistence
Holds only invocation selection values.

## Dependencies And Integration Points
Used by datanode list, usage, and decommission status commands.

## Risks And Test Signals
The arg group multiplicity allows no selector; some consumers require one via a subclass arg group. Tests should cover exclusivity, deprecated aliases, precedence, default empty strings, and command-specific unsupported selector handling.
