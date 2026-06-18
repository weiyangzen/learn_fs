# sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/local/TestLocalOzoneClusterConfig.java

## Purpose
Unit tests for the local cluster configuration value object and format-mode parser.

## Important APIs, types, and functions
Uses `LocalOzoneClusterConfig`, its `Builder`, `FormatMode`, default constants, JUnit assertions, `Paths`, and `Duration`.

## Control flow
Tests build default and overridden configs, compare all getter values, verify string default constants parse to typed defaults, parse user-facing format mode values, and reject unknown/null modes.

## State and persistence behavior
No persistent state. Path defaults and overrides are normalized to absolute paths.

## Dependencies and integration points
Validates the model consumed by `OzoneLocal.RunCommand` and future local runtime implementations.

## Risks and edge cases
Does not cover null builder setters except format mode parser null. Numeric validation is intentionally tested in `TestOzoneLocal`, not here.

## Test signals
Exact values for data dir, mode, datanodes, hosts, ports, S3 defaults, timeout, and parser exceptions.
