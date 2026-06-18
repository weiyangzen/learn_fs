# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/local/LocalOzoneClusterConfig.java

## Purpose
Immutable configuration model for an internal local Ozone cluster runtime.

## Important APIs, types, and functions
Defines defaults for data directory, format mode, datanode count, host/bind host, service ports, S3 gateway, ephemeral cleanup, startup timeout, and local S3 credentials. Exposes getters, `builder()`, `builder(Path)`, `FormatMode`, and a fluent `Builder`.

## Control flow
Builder methods collect values; `build` constructs an immutable config, normalizing the data directory and null-checking object fields. `FormatMode.fromString` trims, uppercases, converts hyphens to underscores, and delegates to enum lookup.

## State and persistence behavior
No runtime persistence. The config describes future runtime state such as storage formatting and whether data should be removed on shutdown.

## Dependencies and integration points
Consumed by `OzoneLocal.RunCommand` and the `LocalOzoneRuntime` contract. Defaults are mirrored as string constants for picocli annotation defaults.

## Risks and edge cases
Builder does not validate ranges; validation is in CLI code. Null setter values fail at build time. Default local credentials are only suitable for local/demo use.

## Test signals
Tests verify defaults, string defaults matching typed defaults, explicit overrides, and format-mode parsing/rejection.
