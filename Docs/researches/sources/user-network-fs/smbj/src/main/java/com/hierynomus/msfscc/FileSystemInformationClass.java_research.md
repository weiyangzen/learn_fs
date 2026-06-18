# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/FileSystemInformationClass.java

Source read signal: reviewed complete local file (46 lines, 1422 bytes).

## Purpose
`FileSystemInformationClass.java` covers filesystem information class enum. enumerates SMB filesystem information query/set classes.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
No flow beyond enum values.

## State and persistence
No mutable state.

## Dependencies and integration points
Used by filesystem metadata request builders/parsers.

## Risks
Wrong values query incompatible response structures.

## Test signals
Signals are filesystem information query tests when present.
