# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceType.java

Source read signal: reviewed complete local file (51 lines, 1764 bytes).

## Purpose
`AceType.java` covers ACE type enum. enumerates supported access allowed/denied, object, callback, audit, mandatory label, resource attribute, and scoped policy ACE types.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
No flow beyond values.

## State and persistence
No mutable state.

## Dependencies and integration points
Used by dispatch in `ACE` and factories in `AceTypes`.

## Risks
Unsupported future ACE types currently fail parsing.

## Test signals
Signals are parse dispatch coverage for every enum value.
