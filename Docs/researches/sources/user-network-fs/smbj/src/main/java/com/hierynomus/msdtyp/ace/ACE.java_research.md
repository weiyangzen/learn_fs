# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/ACE.java

Source read signal: reviewed complete local file (116 lines, 3941 bytes).

## Purpose
`ACE.java` covers abstract ACE base. handles common ACE header/body read-write dispatch for all supported ACE families.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Write reserves four header bytes, writes subclass body, backfills header size; read parses `AceHeader`, dispatches by `AceType`, and advances to `start + aceSize`.

## State and persistence
State is the `AceHeader` plus subclass fields.

## Dependencies and integration points
Integrates with `ACL`, SID, GUID helpers, and access mask enums.

## Risks
Wrong dispatch mapping corrupts security descriptors. Unknown ACE types throw instead of preserving opaque ACEs.

## Test signals
Signals are ACE binary roundtrips for every supported type.
