# sources/storage-engines/tikv/.config/nextest.toml

## Purpose
This Nextest configuration defines TiKV's `ci` test profile behavior.

## Important APIs, types, and functions
The `[profile.ci]` table sets `retries = 2`, disables fail-fast, sets a slow timeout of 60 seconds with termination after 2 periods, and limits failure output to final output. `[profile.ci.junit]` writes `junit.xml`.

## Control flow
Nextest reads this declarative configuration when invoked with the `ci` profile. There is no executable control flow in the file.

## State and persistence behavior
It causes test retry behavior and JUnit XML output. It does not persist application state.

## Dependencies and integration points
It integrates with `cargo nextest` and CI systems that collect JUnit output.

## Risks and edge cases
Retries can hide flaky tests if CI only inspects final success. Slow-timeout settings may terminate legitimate long-running tests. The JUnit path is fixed relative to the invocation directory.

## Test signals
Run `cargo nextest run --profile ci` and verify retries, non-fail-fast behavior, timeout handling, and `junit.xml` generation.
