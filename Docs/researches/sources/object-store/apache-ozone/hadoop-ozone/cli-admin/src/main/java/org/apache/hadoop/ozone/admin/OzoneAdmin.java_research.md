# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/OzoneAdmin.java

## Purpose
Defines the `ozone admin` CLI entrypoint and extensible parent command for admin operations.

## Important APIs, Types, And Functions
`OzoneAdmin` extends `Shell` and implements `ExtensibleParentCommand`. `main` runs the shell. `subcommandType()` returns `AdminSubcommand.class`, enabling service-loaded admin subcommands.

## Control Flow
The JVM entrypoint instantiates `OzoneAdmin` and delegates argument parsing/execution to `Shell.run`. The shell discovers implementations of `AdminSubcommand` and registers them as children.

## State And Persistence
No persistent state is stored. It owns command-line configuration context inherited from `Shell`.

## Dependencies And Integration Points
Integrates all `@MetaInfServices(AdminSubcommand.class)` command groups in this module and elsewhere.

## Risks And Test Signals
Changing `subcommandType` or annotations would break command discovery. Tests should cover main invocation, alias `admin`, help output, and service-loaded child command availability.
