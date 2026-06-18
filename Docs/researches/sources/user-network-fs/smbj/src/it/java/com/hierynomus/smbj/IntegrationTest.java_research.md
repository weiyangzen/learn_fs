# sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/IntegrationTest.java

Source read signal: reviewed complete local file (112 lines, 5289 bytes).

## Purpose
`IntegrationTest.java` covers basic SMB integration tests. covers connection, authentication, share connection, listing empty shares with empty or null paths, disabled signing configuration, and idempotent connection close.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Parameterized tests open clients through `SambaContainer`, authenticate with default credentials, connect to `user`, and assert tree IDs, connected flags, and `.`/`..` directory entries.

## State and persistence
Runtime state is live connection/session/tree state and the empty `user` share.

## Dependencies and integration points
Depends on `SMBClient`, `Connection`, `Session`, `DiskShare`, `SmbConfig`, and container auth setup.

## Risks
Assertions about exact empty-share size depend on Samba listing `.` and `..` and no leftover files from other tests.

## Test signals
Signals are successful session establishment and clean list/close behavior across default config variants.
