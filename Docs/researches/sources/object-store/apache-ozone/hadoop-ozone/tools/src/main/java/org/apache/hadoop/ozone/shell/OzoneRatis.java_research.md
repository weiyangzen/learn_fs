# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/shell/OzoneRatis.java

## Purpose
Wrapper command `ozone ratis` that delegates to Apache Ratis shell under Ozone CLI/tracing infrastructure.

## Important APIs, types, and functions
Extends `GenericCli`, overrides `execute`, initializes `TracingUtil`, creates `RatisShell`, and runs argv through it.

## Control flow
`main` invokes GenericCli. `execute` initializes tracing with the current Ozone config, creates a span named from the command arguments, constructs `RatisShell(System.out)`, and returns its exit code.

## State and persistence behavior
No persistent state. Ratis subcommands may read/write files depending on arguments, as shown by raft-meta-conf tests.

## Dependencies and integration points
Integrates Ozone CLI command discovery with Ratis shell commands. A TODO notes future use of RatisShell.Builder for TLS/conf support.

## Risks and edge cases
Current shell construction does not wire Ozone TLS or other configs into Ratis. Span name lacks a space between `ratis` and joined args.

## Test signals
Tests verify base usage output and local raft-meta-conf subcommand behavior, including generated protobuf file content and parse errors.
