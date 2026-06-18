# sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/SMB2DirectoryIntegrationTest.java

Source read signal: reviewed complete local file (143 lines, 7238 bytes).

## Purpose
`SMB2DirectoryIntegrationTest.java` covers SMB2 directory integration tests. checks opening directories, folder-exists semantics, directory listing, delete-pending handling for rmdir/folderExists, and creating/listing a new directory.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Tests connect to `public` or `user`, use `openDirectory`, `folderExists`, `rmdir`, `deleteOnClose`, `mkdir`, and `list` assertions.

## State and persistence
State is temporary directories and files in the `user` share plus seeded public folder data.

## Dependencies and integration points
Depends on SMB2 create dispositions, access masks, share access, directory information parsing, and Samba delete-pending responses.

## Risks
Delete-pending behavior is server-specific. Cleanup must remove created directories or later empty-share tests can fail.

## Test signals
Signals are correct `Directory` instances, folder/file distinction, stable listing, and no exceptions for delete-pending cases.
