# sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/conf/TestGetConfOptions.java

## Purpose
Tests command aliases and output behavior for `ozone getconf`.

## Important APIs, types, and functions
Uses `OzoneGetConf`, `GenericTestUtils.PrintStreamCapturer`, SCM and OM config keys, and `IOUtils.closeQuietly`.

## Control flow
Static setup captures stdout, creates one command instance, and sets OM node id, OM service ID, and SCM names. Each test runs alias and non-alias forms, resets captured output, and asserts exact strings.

## State and persistence behavior
Mutates only in-memory `OzoneConfiguration` on the command object and process stdout capture state.

## Dependencies and integration points
Tests picocli subcommand aliases for conf key, SCM host listing, and OM host listing.

## Risks and edge cases
The same command instance is shared across tests; output reset avoids leakage but config persists intentionally. OM manager output is asserted empty for incomplete HA config, which may change if validation behavior changes.

## Test signals
Exact stdout: `localhost` for SCM names, `1` for OM node id, and empty OM host listing.
