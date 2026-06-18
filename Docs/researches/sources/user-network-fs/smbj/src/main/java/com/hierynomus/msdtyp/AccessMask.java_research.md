# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/AccessMask.java

Source read signal: reviewed complete local file (82 lines, 2365 bytes).

## Purpose
`AccessMask.java` covers SMB/MS-DTYP access-mask enum. enumerates standard, generic, directory, file, and pipe/printer access bits using `EnumWithValue`.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
No flow beyond enum construction and `getValue()`.

## State and persistence
No mutable state.

## Dependencies and integration points
Used throughout create/open calls, ACE factories, and security descriptors.

## Risks
Missing or wrong bit values cause authorization, create, and ACE serialization bugs.

## Test signals
Signals are open/share integration tests and ACE serialization tests.
