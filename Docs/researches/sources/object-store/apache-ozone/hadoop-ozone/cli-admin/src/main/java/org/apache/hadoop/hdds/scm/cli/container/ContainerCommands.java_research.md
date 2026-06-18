# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/ContainerCommands.java

## Purpose
Registers the `container` command group for SCM container operations.

## Important APIs, Types, And Functions
`ContainerCommands` implements `AdminSubcommand`, uses `@Command(name = "container")`, and declares list, info, create, close, report, upgrade, and reconcile subcommands.

## Control Flow
It has no runtime logic; picocli handles subcommand dispatch after service-loader discovery.

## State And Persistence
No state is held or persisted.

## Dependencies And Integration Points
Integrates with `OzoneAdmin` via `@MetaInfServices(AdminSubcommand.class)`.

## Risks And Test Signals
Command visibility depends on this registration. Tests should verify admin help and each child command route.
