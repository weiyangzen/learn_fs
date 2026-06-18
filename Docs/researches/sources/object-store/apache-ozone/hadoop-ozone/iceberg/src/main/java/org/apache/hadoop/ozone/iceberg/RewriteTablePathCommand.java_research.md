# sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/main/java/org/apache/hadoop/ozone/iceberg/RewriteTablePathCommand.java

## Purpose
`RewriteTablePathCommand` is the CLI front end for rewriting Iceberg table paths during Ozone-backed table migration.

## Important APIs, types, and functions
Required options are `--table-location`, `--source-prefix`, and `--target-prefix`. Optional flags include `--staging`, `--start-version`, `--end-version`, and `--threads` defaulting to 10. `call()` loads the table with `HadoopTables(getOzoneConf())`, creates `RewriteTablePathOzoneAction`, applies options, executes, and prints the latest version, staging location, and file-list location.

## Control flow
The command prints progress, loads the Iceberg table, configures the action fluently, executes it, and returns null on success.

## State and persistence behavior
State is Picocli-populated option fields. The command itself does not write files, but the action writes staged metadata/manifests and file-list output.

## Dependencies and integration points
It extends `AbstractSubcommand` for output/configuration and uses Iceberg `HadoopTables` and `RewriteTablePath`.

## Risks and edge cases
The help text says zero threads uses default 10, but the command passes zero through to the action; the action creates a fixed thread pool with the provided value, so zero would fail. Input strings are trimmed only for table loading, not prefixes.

## Test signals
`TestRewriteTablePathOzoneAction` invokes this command and asserts output contains startup, loaded table, staging, and file-list lines.
