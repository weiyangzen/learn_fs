# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/StatusSubCommand.java

## Purpose
Registers the `ozone admin datanode status` subgroup.

## Important APIs, Types, And Functions
`StatusSubCommand` is a picocli command with one child, `DecommissionStatusSubCommand`.

## Control Flow
No runtime logic exists in this class; picocli dispatches to child status commands.

## State And Persistence
No state is held.

## Dependencies And Integration Points
Nested under `DatanodeCommands`; uses `HddsVersionProvider` for CLI version help.

## Risks And Test Signals
Tests should verify `datanode status decommission` remains reachable and help output lists it.
