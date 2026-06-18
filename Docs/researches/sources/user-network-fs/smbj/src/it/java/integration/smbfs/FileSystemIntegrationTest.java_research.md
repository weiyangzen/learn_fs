# sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileSystemIntegrationTest.java

Source read signal: reviewed complete local file (45 lines, 1554 bytes).

## Purpose
`FileSystemIntegrationTest.java` covers SmbFileSystem creation/close. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
creates a filesystem for the user URI and asserts it is a `SmbFileSystem` instance.

## State and persistence
only live filesystem/session state

## Dependencies and integration points
SmbFiles.newFileSystem and provider lifecycle

## Risks
resource leaks would show up as hanging container sessions or close failures

## Test signals
non-null filesystem of expected type
