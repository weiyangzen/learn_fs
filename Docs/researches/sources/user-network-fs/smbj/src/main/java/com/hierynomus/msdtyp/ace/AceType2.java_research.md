# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceType2.java

Source read signal: reviewed complete local file (142 lines, 4211 bytes).

## Purpose
`AceType2.java` covers object ACE implementation. represents object ACEs with access mask, object/inherited-object GUID flags, optional GUIDs, and SID.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Read parses flags, optional GUIDs using `MsDataTypes`, then SID; write emits only GUIDs selected by flags.

## State and persistence
State is access mask, object flags, optional UUIDs, and SID.

## Dependencies and integration points
Used for access allowed/denied object ACEs and as the base for callback object ACEs.

## Risks
Size/position handling is sensitive because optional GUIDs change body length.

## Test signals
Signals are object ACE roundtrips with each flag combination.
