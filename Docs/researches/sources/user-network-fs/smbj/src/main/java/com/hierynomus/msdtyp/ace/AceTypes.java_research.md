# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceTypes.java

Source read signal: reviewed complete local file (151 lines, 6762 bytes).

## Purpose
`AceTypes.java` covers ACE factory helpers. provides static constructors for common ACE variants from flag sets, access-mask sets, SIDs, UUIDs, and application data.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Each helper creates the appropriate header type and subclass body, converting enum sets to numeric masks where needed.

## State and persistence
Stateless factory utility.

## Dependencies and integration points
Used by callers constructing ACL/security descriptors programmatically.

## Risks
Factory coverage is incomplete for every possible ACE type and must set header/body combinations accurately.

## Test signals
Signals are factory-created ACE write/read roundtrips and descriptor construction tests.
