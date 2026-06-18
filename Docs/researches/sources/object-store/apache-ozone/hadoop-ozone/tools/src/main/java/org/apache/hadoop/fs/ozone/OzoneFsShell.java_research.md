# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/fs/ozone/OzoneFsShell.java

## Purpose
Ozone-specific `FsShell` entry point backing `ozone fs` commands.

## Important APIs, types, and functions
Extends Hadoop `FsShell`, registers default `FsCommand` classes and then `OzoneFsDelete`, customizes usage prefix, initializes tracing, and exposes `getCommandFactory` for tests.

## Control flow
`main` creates an `OzoneConfiguration`, initializes tracing, sets quiet mode false, installs the config, wraps `ToolRunner.run` inside `TracingUtil.executeInNewSpan`, and exits with the shell result. Command registration only happens when the runtime class is exactly `OzoneFsShell`.

## State and persistence behavior
No persistent state is owned by the shell. It configures runtime command registry and tracing span state, and commands may mutate filesystem state.

## Dependencies and integration points
Integrates Hadoop FsShell/ToolRunner, HDDS tracing, Ozone configuration, and the Ozone delete override.

## Risks and edge cases
Exact-class registration guard can surprise subclasses. `System.exit` in `main` makes direct invocation unsuitable for embedded tests. Span naming concatenates user args into tracing data.

## Test signals
`TestOzoneFsShell` confirms `-rm` resolves to `OzoneFsDelete.Rm` and command metadata is available after shell execution.
