# sources/user-network-fs/smbj/src/it/java/integration/smbfs/DirectoryListingIntegrationTest.java

Source read signal: reviewed complete local file (85 lines, 2867 bytes).

## Purpose
`DirectoryListingIntegrationTest.java` covers root and nested directory listing through `SmbFiles`. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
lists root directories and a seeded public folder, collecting path names and comparing ordered expected values.

## State and persistence
read-only traversal of seeded public data

## Dependencies and integration points
SmbFiles, SmbFileSystem, Java streams

## Risks
ordering assumptions can vary if the provider or server changes listing sort behavior

## Test signals
expected root `\` and seeded directory names are returned
