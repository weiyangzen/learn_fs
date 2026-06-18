# sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileAccessIntegrationTest.java

Source read signal: reviewed complete local file (86 lines, 2709 bytes).

## Purpose
`FileAccessIntegrationTest.java` covers NIO `checkAccess` behavior. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
parameterized existing paths should pass while a missing path throws `IOException`.

## State and persistence
read-only access to public seeded files

## Dependencies and integration points
SmbPath and provider access checks

## Risks
server-specific errors must map to Java IO failures consistently

## Test signals
existing file/folder paths pass and missing path fails
