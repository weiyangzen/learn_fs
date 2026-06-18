# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DatanodeCommands.java

## Purpose
Registers the `datanode` admin command group.

## Important APIs, Types, And Functions
`DatanodeCommands` implements `AdminSubcommand`, is annotated with `@Command(name = "datanode")`, and declares list, decommission, maintenance, recommission, status, usageinfo, and diskbalancer subcommands.

## Control Flow
No executable logic exists; picocli dispatches to child commands after service discovery.

## State And Persistence
No state is held.

## Dependencies And Integration Points
Integrates with `OzoneAdmin` via `@MetaInfServices(AdminSubcommand.class)`.

## Risks And Test Signals
Command discovery and help output should be tested to catch accidental registration loss.
