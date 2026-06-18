# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/SafeModeCommands.java

## Purpose
Registers the `safemode` command group for SCM safe mode operations.

## Important APIs, Types, And Functions
`SafeModeCommands` implements `AdminSubcommand`, is annotated with picocli `@Command(name = "safemode")`, and declares `SafeModeCheckSubcommand`, `SafeModeExitSubcommand`, and `SafeModeWaitSubcommand` as subcommands. `@MetaInfServices(AdminSubcommand.class)` makes it discoverable by `OzoneAdmin`.

## Control Flow
There is no executable command logic in the class. Picocli dispatches to the selected child command after service-loader discovery.

## State And Persistence
No state is held or persisted.

## Dependencies And Integration Points
Depends on `AdminSubcommand`, `HddsVersionProvider`, picocli, and `org.kohsuke.MetaInfServices`.

## Risks And Test Signals
The main risk is registration drift: removing a child or annotation makes commands disappear. Test signals are CLI help output and service-loader command discovery for `ozone admin safemode`.
