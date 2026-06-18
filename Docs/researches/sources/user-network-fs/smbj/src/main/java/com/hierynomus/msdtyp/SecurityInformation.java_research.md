# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/SecurityInformation.java

Source read signal: reviewed complete local file (46 lines, 1566 bytes).

## Purpose
`SecurityInformation.java` covers security information selector enum. enumerates owner/group/DACL/SACL/label/attribute/scope bits requested in SMB security operations.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
No flow beyond `getValue()`.

## State and persistence
No mutable state.

## Dependencies and integration points
Used by security descriptor query/set request builders.

## Risks
Incorrect bit values request or update the wrong security sections.

## Test signals
Signals are get/set security request tests.
