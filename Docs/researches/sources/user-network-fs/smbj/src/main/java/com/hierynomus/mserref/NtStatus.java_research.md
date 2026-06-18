# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mserref/NtStatus.java

Source read signal: reviewed complete local file (170 lines, 5342 bytes).

## Purpose
`NtStatus.java` covers NTSTATUS enum/helper. maps many SMB/Windows NTSTATUS codes to enum constants and classifies success, informational, warning, and error ranges.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
`valueOf(long)` returns a matching constant or `STATUS_OTHER`; classification methods inspect high bits/status ranges.

## State and persistence
No mutable state beyond enum values.

## Dependencies and integration points
Used by SMB exception mapping and integration tests expecting statuses such as sharing violation.

## Risks
Incomplete enum coverage falls back to `STATUS_OTHER`, which can hide specific server behavior.

## Test signals
Signals are status mapping tests and integration assertions on expected status codes.
