# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileAccessInformation.java

Source read signal: reviewed complete local file (29 lines, 920 bytes).

## Purpose
`FileAccessInformation.java` covers file access information DTO. holds access flags returned by a file information query.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
The class exposes `getAccessFlags()` and is populated by the file information parser infrastructure.

## State and persistence
State is one integer access mask.

## Dependencies and integration points
Integrates with MS-FSCC file information query machinery.

## Risks
Very small DTO; correctness depends on external parser setting the field with little-endian data.

## Test signals
Signals are file information query tests for access masks.
