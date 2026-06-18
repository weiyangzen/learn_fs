# sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileMoveIntegrationTest.java

Source read signal: reviewed complete local file (125 lines, 4860 bytes).

## Purpose
`FileMoveIntegrationTest.java` covers NIO move/rename behavior. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
moves files within one share, verifies overwrite failure, and moves from public to user while removing the source.

## State and persistence
temporary source/target files and helper directories in public/user shares

## Dependencies and integration points
provider.move, SMB status-to-exception mapping, container probes

## Risks
overwrite semantics and cross-share source deletion are important correctness boundaries

## Test signals
target content preserved, source absent for cross-share move, overwrite throws
