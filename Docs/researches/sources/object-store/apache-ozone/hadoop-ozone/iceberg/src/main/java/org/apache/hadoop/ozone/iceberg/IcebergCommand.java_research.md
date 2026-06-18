# sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/main/java/org/apache/hadoop/ozone/iceberg/IcebergCommand.java

## Purpose
`IcebergCommand` is the Picocli root command for Ozone Iceberg table utilities.

## Important APIs, types, and functions
The `@Command` annotation names the command `ozone iceberg`, adds alias `iceberg`, uses `HddsVersionProvider`, enables standard help options, and registers `RewriteTablePathCommand` as a subcommand. `main` runs the command through `GenericCli`.

## Control flow
Picocli dispatches subcommands; this class only boots the CLI.

## State and persistence behavior
No runtime state is stored by this class.

## Dependencies and integration points
It extends HDDS `GenericCli`, so it inherits Ozone configuration and command execution behavior. Tests execute `new IcebergCommand().getCmd().execute(...)`.

## Risks and edge cases
Command naming and aliases must remain stable for users and scripts. Adding subcommands requires updating the annotation.

## Test signals
`TestRewriteTablePathOzoneAction` uses this command to run the `rewrite-path` subcommand and assert exit code/output.
