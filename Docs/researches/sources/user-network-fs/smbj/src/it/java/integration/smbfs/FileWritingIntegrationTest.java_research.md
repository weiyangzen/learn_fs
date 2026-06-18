# sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileWritingIntegrationTest.java

Source read signal: reviewed complete local file (112 lines, 3735 bytes).

## Purpose
`FileWritingIntegrationTest.java` covers NIO writing and appending. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
writes a new file, appends to an empty file, and appends to an existing file, then verifies contents from the container.

## State and persistence
temporary `written.txt` and `test.txt` under user share

## Dependencies and integration points
provider.newOutputStream, `StandardOpenOption.APPEND`, Testcontainers file reads

## Risks
append mode must not truncate and file permissions from copied fixture must allow writes

## Test signals
container file content matches expected concatenation
