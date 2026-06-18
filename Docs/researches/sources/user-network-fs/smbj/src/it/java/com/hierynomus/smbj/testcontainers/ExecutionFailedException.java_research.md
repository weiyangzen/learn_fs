# sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/testcontainers/ExecutionFailedException.java

Source read signal: reviewed complete local file (24 lines, 873 bytes).

## Purpose
`ExecutionFailedException.java` covers Testcontainers exec failure exception. wraps a failed container exec exit code in a runtime exception used by `SambaContainer.ensureOk()`.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Constructed when helper commands such as `mkdir`, `chmod`, or `rm` return non-zero.

## State and persistence
No persistent state beyond the exit code in the message/field.

## Dependencies and integration points
Integrates with Testcontainers `execInContainer` helper methods.

## Risks
Only exit code is captured, so stderr/stdout context can be lost.

## Test signals
Signals are helper tests or integration setup failures surfacing a clear non-zero exit.
