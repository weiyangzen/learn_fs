# sources/user-network-fs/smbj/src/it/java/integration/smbfs/DirectoryCreationIntegrationTest.java

Source read signal: reviewed complete local file (52 lines, 1674 bytes).

## Purpose
`DirectoryCreationIntegrationTest.java` covers directory creation through the NIO provider. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
opens a `SmbFileSystem` from `samba.userUri()`, calls `provider().createDirectory()` on path `a`, and relies on cleanup by container state isolation.

## State and persistence
temporary directory `a` in the user share

## Dependencies and integration points
SmbFileSystemProvider, SmbPath, and Testcontainers

## Risks
cleanup omissions can affect later tests if the share is reused

## Test signals
directory visible in the container/user share after creation
