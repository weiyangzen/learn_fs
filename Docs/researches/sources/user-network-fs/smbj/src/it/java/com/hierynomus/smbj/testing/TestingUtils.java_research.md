# sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/testing/TestingUtils.java

Source read signal: reviewed complete local file (94 lines, 3660 bytes).

## Purpose
`TestingUtils.java` covers shared integration-test utilities. defines credentials, authentication contexts, random helpers, config parameter streams for default and DFS tests, EOF comparison helper, and checked callback interfaces.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
JUnit `@MethodSource` providers build `SmbConfig` variants for dialect/sign/encrypt/DFS combinations; tests use static credentials and helper methods to reduce setup duplication.

## State and persistence
State includes a shared `Random` and constants for username/password/domain.

## Dependencies and integration points
Integrates JUnit parameterized tests, SMBJ auth/config APIs, file IO helpers, and the Samba container.

## Risks
Shared random state is non-deterministic. Expanding config matrices increases test runtime and can expose server feature mismatches.

## Test signals
Signals are broad reuse across integration tests and parameterized coverage of config variants.
