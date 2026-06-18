# sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileCopyIntegrationTest.java

Source read signal: reviewed complete local file (87 lines, 3169 bytes).

## Purpose
`FileCopyIntegrationTest.java` covers NIO copy within and across SMB shares. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
copies a generated source file on the same share and from public to user, then verifies target contents from inside the container.

## State and persistence
temporary source/target files under `/opt/samba/user` and `/opt/samba/share`

## Dependencies and integration points
SmbFileSystemProvider.copy, Testcontainers file copy helpers

## Risks
cross-share copy may fall back to client-side streaming and must preserve bytes

## Test signals
container target file content equals original random data
