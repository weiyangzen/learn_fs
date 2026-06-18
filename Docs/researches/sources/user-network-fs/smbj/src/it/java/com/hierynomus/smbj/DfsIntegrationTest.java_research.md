# sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/DfsIntegrationTest.java

Source read signal: reviewed complete local file (99 lines, 4769 bytes).

## Purpose
`DfsIntegrationTest.java` covers DFS share integration tests. validates smbj DFS resolution against the container's `dfs` share, including virtual directory listing, broken-first-target fallback, and filename preservation for normal shares when DFS is enabled.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Tests use `TestingUtils#dfsConfig`, connect to `dfs`, list links, open DFS directories through helper `withDir()`, and assert regular share directory path/name/UNC fields.

## State and persistence
State comes from DFS symlinks created by the entrypoint and temporary directory handles.

## Dependencies and integration points
Depends on the MSDFS-enabled Samba config, `SambaContainer`, `Directory`, `DiskShare`, DFS client path rewriting, and file information listings.

## Risks
DFS target hostnames/loopback choices are environment-sensitive. Fallback behavior relies on a reserved unreachable address followed by a good target.

## Test signals
Signals are listed DFS links, successful fallback listing, and unchanged regular-share `getFileName()`/UNC behavior.
