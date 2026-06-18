# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceObjectFlags.java

Source read signal: reviewed complete local file (35 lines, 1038 bytes).

## Purpose
`AceObjectFlags.java` covers object ACE flag enum. defines object-type and inherited-object-type GUID presence bits.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
No flow beyond enum values.

## State and persistence
No mutable state.

## Dependencies and integration points
Used by object ACE subclasses.

## Risks
Incorrect flags make GUID fields misread or omitted.

## Test signals
Signals are object ACE roundtrips with zero, one, and both GUIDs.
