# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/FileInformationClass.java

Source read signal: reviewed complete local file (101 lines, 3509 bytes).

## Purpose
`FileInformationClass.java` covers file information class enum. enumerates SMB query/set file information classes with numeric protocol values.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
No flow beyond enum values.

## State and persistence
No mutable state.

## Dependencies and integration points
Used to select parsers and request classes for file metadata operations.

## Risks
Missing values limit protocol coverage; wrong numeric values query the wrong structure.

## Test signals
Signals are directory listing, file ID, internal information, and metadata query tests.
