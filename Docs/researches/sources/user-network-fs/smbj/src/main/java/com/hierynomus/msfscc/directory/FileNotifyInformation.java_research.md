# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/directory/FileNotifyInformation.java

Source read signal: reviewed complete local file (58 lines, 1922 bytes).

## Purpose
`FileNotifyInformation.java` covers change notify information parser. reads one file-notify record containing next-entry offset, action, file-name length, and UTF-16 file name.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
`read()` consumes fields from a generic buffer and maps the action with `EnumWithValue`.

## State and persistence
State is parsed offset, action, and filename.

## Dependencies and integration points
Used by SMB2 change notify response parsing and integration tests.

## Risks
It parses a single record; callers must handle chaining via `nextEntryOffset`. Unknown actions become null.

## Test signals
Signals are change-notify tests and multi-record notify parser tests.
