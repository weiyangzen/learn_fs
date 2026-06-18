# sources/user-network-fs/smbj/src/it/java/integration/smbfs/FileReadingIntegrationTest.java

Source read signal: reviewed complete local file (60 lines, 1909 bytes).

## Purpose
`FileReadingIntegrationTest.java` covers NIO file read. It validates the smbj `smbfs` Java NIO provider against the Samba Testcontainers fixture.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
opens `test.txt` from public with `newInputStream`, reads all bytes, and checks UTF-8 contents.

## State and persistence
read-only seeded public file

## Dependencies and integration points
SmbPath, provider.newInputStream, Java IO

## Risks
assumes fixture content and charset remain stable

## Test signals
read content equals `Hi there!\n`
