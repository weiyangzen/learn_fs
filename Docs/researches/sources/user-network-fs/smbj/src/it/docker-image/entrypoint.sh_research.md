# sources/user-network-fs/smbj/src/it/docker-image/entrypoint.sh

Source read signal: reviewed complete local file (26 lines, 690 bytes).

## Purpose
`entrypoint.sh` covers Samba integration entrypoint. sets default SMB credentials and creates DFS symlinks under `/opt/samba/dfs` before execing the container command.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
It currently hard-codes `ip_address=127.0.0.1`, creates links for `public`, `user`, and `firstfail-public`, then `exec`s supervisord or the passed command.

## State and persistence
Persistent container state is the created msdfs symlinks; credentials are environment defaults consumed earlier by image creation.

## Dependencies and integration points
Integrates with Samba's `msdfs root` share and DFS integration tests that expect working and fallback links.

## Risks
The hard-coded loopback address assumes Samba resolves links from inside the test topology. Re-running can fail if symlinks already exist unless the filesystem is fresh.

## Test signals
Signals are DFS share listings containing `public`, `user`, and fallback behavior for `firstfail-public`.
