# sources/user-network-fs/smbj/src/it/resources/logback-test.xml

Source read signal: reviewed complete local file (32 lines, 1008 bytes).

## Purpose
`logback-test.xml` covers integration-test logging config. sets Logback appenders and logger levels for tests, including SMBJ and Testcontainers output.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Logback loads it from test resources during integration-test runtime.

## State and persistence
No application state; it controls emitted logs.

## Dependencies and integration points
Integrates with SLF4J/Logback and Testcontainers logging.

## Risks
Overly verbose levels can slow large transfers or hide relevant logs in CI noise; overly quiet levels reduce diagnosability.

## Test signals
Signals are useful test logs without excessive output.
