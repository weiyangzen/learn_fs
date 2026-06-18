# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/FileNotifyAction.java

Source read signal: reviewed complete local file (45 lines, 1474 bytes).

## Purpose
`FileNotifyAction.java` covers file notify action enum. maps change-notify action codes such as added, removed, modified, renamed old/new name, stream changes, and security changes.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
No flow beyond `getValue()`.

## State and persistence
No mutable state.

## Dependencies and integration points
Used by `FileNotifyInformation` and change notify responses.

## Risks
Unknown action codes map to null in current parser callers if not handled.

## Test signals
Signals are change notify integration tests expecting `FILE_ACTION_ADDED`.
