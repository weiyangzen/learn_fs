# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceType1.java

Source read signal: reviewed complete local file (67 lines, 1937 bytes).

## Purpose
`AceType1.java` covers simple SID/access-mask ACE implementation. represents ACEs whose body is access mask plus SID, including allowed/denied/audit/mandatory-label/scoped-policy forms.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Write emits access mask and SID; read consumes both from the buffer.

## State and persistence
State is access mask and SID.

## Dependencies and integration points
Used by `ACE.read()` and `AceTypes` simple factory methods.

## Risks
Semantic differences between ACE types are carried only by header type, so callers must set the right header.

## Test signals
Signals are roundtrips for allowed, denied, audit, mandatory label, and scoped policy ACEs.
