# sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileDeleteIntegrationTest.java

Source read signal: reviewed complete local file (72 lines, 2420 bytes).

## Purpose
`FileDeleteIntegrationTest.java` covers NIO delete of files with nested parameter cases. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
copies files into user share, deletes through provider paths, and asserts the container path no longer exists.

## State and persistence
temporary files under `/opt/samba/user` including nested `a/b.txt`

## Dependencies and integration points
provider.delete and SambaContainer file probes

## Risks
directory setup/teardown must match parameterized nested paths

## Test signals
container `test -f` returns false after delete
