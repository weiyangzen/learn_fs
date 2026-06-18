# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/SID.java

Source read signal: reviewed complete local file (203 lines, 7114 bytes).

## Purpose
`SID.java` covers Security Identifier model. parses SID literals, reads/writes binary SIDs, formats numeric SID strings, exposes SID type enum, and defines `EVERYONE`.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
`fromString()` validates with regex, encodes identifier authority into 6 bytes, parses subauthorities; `write()` emits revision/count/authority/subauthorities; `read()` reverses it.

## State and persistence
State is revision, identifier authority byte array, and subauthority array.

## Dependencies and integration points
Used by ACEs, security descriptors, and access-control APIs.

## Risks
Arrays are exposed directly by getters and not defensively copied. `write()` checks too-long authority but not too-short authority.

## Test signals
Signals are SID string/binary roundtrips and security descriptor tests.
