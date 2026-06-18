# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/FileAttributes.java

Source read signal: reviewed complete local file (107 lines, 4711 bytes).

## Purpose
`FileAttributes.java` covers MS-FSCC file attribute enum. defines file attribute bit flags such as readonly, hidden, system, directory, archive, temporary, sparse, reparse point, compressed, encrypted, and integrity flags.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
No flow beyond `getValue()`.

## State and persistence
No mutable state.

## Dependencies and integration points
Used by file information parsing, create options, and attribute integration tests.

## Risks
Wrong bit values misclassify files/directories or corrupt create/set-info requests.

## Test signals
Signals are file attribute parse tests and NIO basic attribute integration tests.
