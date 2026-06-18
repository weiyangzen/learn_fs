# sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/local/TestOzoneLocal.java

## Purpose
Unit tests for hidden `ozone local run` CLI metadata, defaults, parsing, validation, and GenericCli error output.

## Important APIs, types, and functions
Uses `OzoneLocal`, `RunCommand`, `LocalOzoneClusterConfig`, picocli `CommandLine`, reflective access to `@Option` default values, custom `IDefaultValueProvider`, and JUnit assertions.

## Control flow
Tests inspect command annotations, ensure GenericCli registers `run`, capture help output to verify hidden subcommand behavior, execute `run` with no output, validate every environment default expression, resolve defaults through a fallback provider, parse overrides, test ISO and Hadoop-style durations, exercise negatable booleans, and assert parse/config errors.

## State and persistence behavior
No persistent state. Tests mutate command-line parser output/error streams and instantiate command objects.

## Dependencies and integration points
Validates picocli integration with HDDS GenericCli and the `LocalOzoneClusterConfig` builder.

## Risks and edge cases
Reflection ties tests to field names. It does not verify actual environment-variable expansion values from a real environment.

## Test signals
Signals include exact metadata, hidden help behavior, resolved config values, thrown `ParameterException`/`IllegalArgumentException`, and GenericCli exit code `-1` for invalid config.
