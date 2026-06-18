# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceType3.java

Source read signal: reviewed complete local file (79 lines, 2434 bytes).

## Purpose
`AceType3.java` covers callback ACE implementation. represents callback/resource ACEs with access mask, SID, and trailing application data.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Read consumes access mask and SID, then uses ACE size to read remaining application data; write emits all three.

## State and persistence
State is access mask, SID, and byte array application data.

## Dependencies and integration points
Used for callback and resource attribute ACE types.

## Risks
Trailing data length depends on correct `aceStartPos` and header size. Application data is exposed directly.

## Test signals
Signals are callback ACE roundtrips with empty and non-empty data.
