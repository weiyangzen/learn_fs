# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceHeader.java

Source read signal: reviewed complete local file (83 lines, 2401 bytes).

## Purpose
`AceHeader.java` covers ACE header parser/writer. stores ACE type, flags, and size and reads/writes the four-byte ACE header.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Write emits type value, combined flags, and size. Read maps byte values to `AceType` and `AceFlags` set.

## State and persistence
State is type, flag set, and size for one ACE.

## Dependencies and integration points
Used by `ACE.read()` and `ACE.write()`.

## Risks
Unknown ACE type maps to null, later causing dispatch failure. Size must include header and body.

## Test signals
Signals are header roundtrip tests and malformed ACE handling.
