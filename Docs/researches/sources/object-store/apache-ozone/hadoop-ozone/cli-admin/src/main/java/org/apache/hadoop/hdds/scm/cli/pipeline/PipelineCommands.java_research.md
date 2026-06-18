# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/PipelineCommands.java

## Purpose
Registers the `pipeline` SCM admin command group.

## Important APIs, Types, And Functions
`PipelineCommands` implements `AdminSubcommand`, is annotated with `@Command(name = "pipeline")`, and declares list, activate, deactivate, create, and close subcommands.

## Control Flow
No executable logic exists; picocli dispatches to child commands.

## State And Persistence
No state is held.

## Dependencies And Integration Points
Integrates with `OzoneAdmin` via `@MetaInfServices(AdminSubcommand.class)`.

## Risks And Test Signals
Command registration should be covered by CLI help/discovery tests.
