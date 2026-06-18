# sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileAttributesIntegrationTest.java

Source read signal: reviewed complete local file (77 lines, 2748 bytes).

## Purpose
`FileAttributesIntegrationTest.java` covers NIO basic file attribute reads. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
reads `BasicFileAttributes` for a public file and directory and asserts regular/directory flags, size, symlink false, and null file key.

## State and persistence
read-only metadata from public data

## Dependencies and integration points
NIO attributes and SMB file info mapping

## Risks
directory size is asserted as zero, which can be server-dependent

## Test signals
attributes match the seeded `test.txt` and `folder` fixtures
