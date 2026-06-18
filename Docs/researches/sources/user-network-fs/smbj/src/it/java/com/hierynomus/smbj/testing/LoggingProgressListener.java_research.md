# sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/testing/LoggingProgressListener.java

Source read signal: reviewed complete local file (31 lines, 1081 bytes).

## Purpose
`LoggingProgressListener.java` covers test progress logger. implements an SMBJ progress listener that logs transfer progress during integration tests.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Callback methods receive byte counts or progress events and emit them through SLF4J.

## State and persistence
No persistent state beyond logger use.

## Dependencies and integration points
Integrates with SMBJ IO transfer APIs and test logging.

## Risks
High-frequency progress logging can make large-transfer tests noisy.

## Test signals
Signals are readable progress logs when transfer tests fail or time out.
