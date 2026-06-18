# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/MsDataTypes.java

Source read signal: reviewed complete local file (99 lines, 4110 bytes).

## Purpose
`MsDataTypes.java` covers MS-DTYP primitive helpers. reads/writes GUIDs in Microsoft mixed-endian layout and FILETIME values from generic buffers.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
GUID write splits UUID bits into little-endian first fields and big-endian tail; read reverses that; filetime helpers wrap `FileTime`.

## State and persistence
Stateless utility class.

## Dependencies and integration points
Used by ACE object GUIDs, security structures, and other protocol messages.

## Risks
GUID byte order is easy to regress because it differs from network-order UUID text.

## Test signals
Signals are GUID/filetime binary fixture roundtrips.
