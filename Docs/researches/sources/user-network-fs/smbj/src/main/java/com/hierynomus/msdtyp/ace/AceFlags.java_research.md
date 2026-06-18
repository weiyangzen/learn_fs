# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceFlags.java

Source read signal: reviewed complete local file (38 lines, 1133 bytes).

## Purpose
`AceFlags.java` covers ACE inheritance/audit flag enum. defines ACE flag bit values for object/container inheritance, no-propagate, inherit-only, inherited, and audit success/failure.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
No flow beyond enum values.

## State and persistence
No mutable state.

## Dependencies and integration points
Used by `AceHeader` and `AceTypes` factory methods.

## Risks
Bit drift changes inheritance/audit semantics in serialized ACLs.

## Test signals
Signals are ACE header flag parse/write tests.
