# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/local/OzoneLocal.java

## Purpose
Hidden internal CLI entry point `ozone local` with a hidden `run` command that resolves local cluster runtime configuration.

## Important APIs, types, and functions
Extends `GenericCli`. `RunCommand` extends `AbstractSubcommand`, declares options with environment-variable defaults, and resolves a `LocalOzoneClusterConfig`. Nested converters parse `FormatMode` and ISO/Hadoop-style `Duration`.

## Control flow
CLI default values first consult `OZONE_LOCAL_*` environment variables. `RunCommand.call` resolves config quietly. `resolveConfig` validates datanodes >= 1, ports 0..65535, and positive startup timeout, then builds the immutable config.

## State and persistence behavior
No runtime cluster is started here and no persistent state is written. The command only materializes config state for a future runtime.

## Dependencies and integration points
Uses picocli, HDDS `GenericCli`/`AbstractSubcommand`, `TimeDurationUtil`, and `LocalOzoneClusterConfig`.

## Risks and edge cases
Command is hidden, so user-facing stability may be lower. Environment default expressions are duplicated across many constants and tested reflectively. Invalid data-dir parse uses picocli path conversion.

## Test signals
Tests cover hidden metadata, subcommand registration, help hiding, quiet run, env default strings, CLI overrides, duration parsing, negatable booleans, invalid ports/datanodes/durations/paths, legacy option rejection, and error output.
