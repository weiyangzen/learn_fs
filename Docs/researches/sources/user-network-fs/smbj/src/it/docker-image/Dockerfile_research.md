# sources/user-network-fs/smbj/src/it/docker-image/Dockerfile

Source read signal: reviewed complete local file (23 lines, 711 bytes).

## Purpose
`Dockerfile` covers integration-test Samba image. builds an Alpine-based image with tini, Samba, supervisor, bash, a configured `smbj` user, public/user/readonly/dfs directories, copied Samba config, and exposed SMB/NetBIOS ports.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Build flow installs packages, copies configs, adds seed public data, creates directories with permissive modes, creates the Samba user/passdb entry, marks the entrypoint executable, then starts supervisord through tini.

## State and persistence
Container filesystem state includes `/opt/samba/share`, `/opt/samba/user`, `/opt/samba/readonly`, `/opt/samba/dfs`, `/etc/samba/smb.conf`, and the Samba passdb.

## Dependencies and integration points
Used by integration tests and mirrored programmatically by `SambaContainer.Builder`, though the builder uses a newer Alpine base.

## Risks
The static Dockerfile and Java builder can drift. Alpine/Samba package changes affect DFS and auth behavior. Permissive modes are intentional for tests but unsuitable for production.

## Test signals
Signals are successful image build, smbd/nmbd startup, and passing Testcontainers integration tests.
