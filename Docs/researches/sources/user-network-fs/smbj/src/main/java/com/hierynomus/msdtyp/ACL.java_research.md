# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ACL.java

Source read signal: reviewed complete local file (93 lines, 2765 bytes).

## Purpose
`ACL.java` covers MS-DTYP ACL serializer. represents an ACL revision and ACE list, and reads/writes SMB self-relative ACL wire format.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Write reserves ACL size, emits ACE count and ACE bodies, then backfills size. Read consumes revision, size, count, reserved fields, and reads each `ACE`.

## State and persistence
State is revision plus ACE list, with null lists normalized to empty.

## Dependencies and integration points
Integrates with `SecurityDescriptor`, `ACE`, and `SMBBuffer`.

## Risks
Read ignores ACL size for bounds beyond buffer position, so malformed ACE counts can drive buffer errors. Returned ACE list is mutable if caller supplied one.

## Test signals
Signals are security descriptor roundtrips and ACL/ACE fixture parsing.
