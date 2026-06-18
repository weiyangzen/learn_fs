# sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/java/org/apache/hadoop/fs/ozone/TestOzoneFsShell.java

## Purpose
Unit test verifying `OzoneFsShell` registers the Ozone-specific delete command override.

## Important APIs, types, and functions
Uses `OzoneFsShell`, Hadoop `ToolRunner`, `CommandFactory`, `Command`, and `OzoneFsDelete.Rm`. Captures stderr to keep failed shell parse output from polluting test output.

## Control flow
The test runs the shell with invalid dummy arguments to trigger command registration, obtains the command factory, asserts a single `-rm` binding, instantiates it, and checks class and command name.

## State and persistence behavior
No filesystem state is modified; command execution is only used to initialize the registry. System stderr is temporarily redirected and restored.

## Dependencies and integration points
Tests OzoneFsShell integration with Hadoop FsShell command factory and Ozone delete override ordering.

## Risks and edge cases
It does not test actual delete behavior or every registered command. The source path contains `src/test/java/java`, which is unusual but valid if included by build configuration.

## Test signals
Factory non-nullness, exactly one `-rm` command name, instance class `OzoneFsDelete.Rm`, and command name `rm`.
