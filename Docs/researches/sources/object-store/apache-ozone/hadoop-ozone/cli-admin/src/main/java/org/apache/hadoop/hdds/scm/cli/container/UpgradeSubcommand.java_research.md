# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/UpgradeSubcommand.java

## Purpose
Provides a deprecated placeholder for the old `ozone admin container upgrade` command, directing users to the repair command.

## Important APIs, Types, And Functions
The command extends `AbstractSubcommand`, implements `Callable<Void>`, accepts ignored `--volume` and `--yes` options, and always throws `IllegalStateException` from `call()`.

## Control Flow
Any invocation fails immediately with a message pointing to `ozone repair datanode upgrade-container-schema`.

## State And Persistence
No state is read or mutated.

## Dependencies And Integration Points
Maintains backward command discovery under `ContainerCommands` while moving functionality elsewhere.

## Risks And Test Signals
Tests should verify old options remain parseable and invocation fails with the migration message rather than performing any upgrade work.
