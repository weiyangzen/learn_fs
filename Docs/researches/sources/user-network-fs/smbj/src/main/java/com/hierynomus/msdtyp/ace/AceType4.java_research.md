# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/ace/AceType4.java

Source read signal: reviewed complete local file (77 lines, 2615 bytes).

## Purpose
`AceType4.java` covers callback object ACE implementation. extends object ACE handling with trailing application data.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Read delegates object fields then reads remaining bytes as application data according to ACE size.

## State and persistence
State is object ACE fields plus application data.

## Dependencies and integration points
Used for callback object and some audit object ACE dispatch paths.

## Risks
The dispatch maps `SYSTEM_AUDIT_OBJECT_ACE_TYPE` to `AceType4`, which should be checked against spec expectations because non-callback audit object ACEs may not contain application data.

## Test signals
Signals are callback object ACE fixtures and audit object ACE parse tests.
