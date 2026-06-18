# sources/user-network-fs/smbj/src/it/docker-image/supervisord.conf

Source read signal: reviewed complete local file (14 lines, 397 bytes).

## Purpose
`supervisord.conf` covers test container process supervisor config. runs `smbd --daemon --foreground --configfile=/etc/samba/smb.conf` and `nmbd --daemon --foreground` with supervisord in the foreground.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Supervisord starts both Samba daemons and keeps the container alive; tini is PID 1 in the Dockerfile/builder.

## State and persistence
No application state, only supervisor process and logs.

## Dependencies and integration points
Integrates with the container entrypoint and Testcontainers wait-for-port behavior.

## Risks
If smbd forks unexpectedly or exits after binding, the listening-port wait can be insufficient to prove share readiness. nmbd failures may be less visible.

## Test signals
Signals are container logs, port 445 listening, and successful SMB session establishment.
