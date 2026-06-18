# sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/AnonymousIntegrationTest.java

Source read signal: reviewed complete local file (104 lines, 5279 bytes).

## Purpose
`AnonymousIntegrationTest.java` covers anonymous/guest SMB integration tests. parameterized tests authenticate with `AuthenticationContext.anonymous()`, verify signing-required failure, and connect to the guest `public` share.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Each test uses `SambaContainer.INSTANCE`, `withConnectedClient()`, or manual `SMBClient` connection, then asserts session IDs, guest signing exceptions, and `DiskShare` tree state.

## State and persistence
State is limited to live SMB sessions/tree connects against the container.

## Dependencies and integration points
Depends on Testcontainers, JUnit Jupiter parameter sources from `TestingUtils`, SMB dialect/sign/encrypt config variants, and `SambaContainer`.

## Risks
Guest auth behavior is sensitive to Samba `map to guest`, signing policy, and dialect negotiation.

## Test signals
Passing tests signal anonymous login, expected signing enforcement, and guest share connectivity.
