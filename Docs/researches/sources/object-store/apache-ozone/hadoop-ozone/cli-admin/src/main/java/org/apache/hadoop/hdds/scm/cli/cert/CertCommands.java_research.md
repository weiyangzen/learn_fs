# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/CertCommands.java

## Purpose
Registers the `cert` command group for SCM CA certificate operations.

## Important APIs, Types, And Functions
`CertCommands` implements `AdminSubcommand`, uses picocli `@Command(name = "cert")`, and declares `InfoSubcommand`, `ListSubcommand`, and `CleanExpiredCertsSubcommand`. `@MetaInfServices` exposes it to the admin CLI.

## Control Flow
The class has no executable logic; picocli dispatches to child commands.

## State And Persistence
No state is held or persisted.

## Dependencies And Integration Points
Integrates with `OzoneAdmin` via the `AdminSubcommand` service-loader mechanism.

## Risks And Test Signals
Test CLI help and command discovery to ensure certificate subcommands remain registered.
