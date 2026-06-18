# sources/user-network-fs/smbj/src/it/docker-image/smb.conf

Source read signal: reviewed complete local file (62 lines, 1189 bytes).

## Purpose
`smb.conf` covers Samba test configuration. defines a standalone user-security Samba server with guest mapping, Japanese DOS charset CP932, high auth logging, MSDFS host support, and `public`, `readonly`, `user`, and `dfs` shares.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Samba reads global options at daemon start and serves shares from `/opt/samba/*`; the `dfs` share is read-only, public, guest-ok, and marked `msdfs root = yes`.

## State and persistence
State lives in Samba TDB passdb, share directories, logs under `/var/log/samba.log`, and DFS symlink targets.

## Dependencies and integration points
Consumed by smbd/nmbd in the Docker image and by all smbj integration tests.

## Risks
The `interfaces = 192.168.2.0/24 eth0` plus `bind interfaces only = yes` is topology-sensitive. Guest-only public access and permissive create modes are test-specific.

## Test signals
Signals are authenticated access to `user`, anonymous access to `public`, denied writes to `readonly`, and working DFS referrals.
