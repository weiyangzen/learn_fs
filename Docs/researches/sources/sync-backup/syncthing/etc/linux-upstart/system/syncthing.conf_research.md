# sources/sync-backup/syncthing/etc/linux-upstart/system/syncthing.conf

## Purpose
This Upstart system job template runs Syncthing as a system-managed service for a configured user. It targets older Linux distributions using Upstart.

## Important APIs, Types, And Functions
The job uses Upstart stanzas: `description`, `start on`, `stop on`, `env`, `setuid`, `setgid`, `exec`, and `respawn`. It sets `STNORESTART=yes`, `HOME=/home/$USER`, runs as `$USER`, executes `/usr/local/bin/syncthing`, and respawns on failure.

## Control Flow
Upstart starts the job when local filesystems are available and a non-loopback network device comes up. It stops outside runlevels 2-5. The service runs Syncthing directly; `STNORESTART=yes` disables Syncthing's own monitor restart behavior so Upstart owns respawn behavior.

## State And Persistence Behavior
Syncthing state is tied to `HOME=/home/$USER` and the configured Unix user. The job itself has no logfile path; logging depends on Upstart's handling of job stdout/stderr and Syncthing defaults.

## Dependencies And Integration Points
It integrates with Upstart event names, Linux runlevels, user/group privileges, and the Syncthing binary at `/usr/local/bin/syncthing`. It is an alternative to systemd/runit templates.

## Risks And Edge Cases
`$USER` must be provided by job configuration or environment; if not, `HOME`, `setuid`, and `setgid` are invalid or surprising. The `exec` command does not include modern `serve` subcommand flags, so behavior depends on Syncthing CLI compatibility with legacy invocation. Upstart itself is legacy on most current Linux distributions.

## Test Signals
Testing requires an Upstart system: configure `USER`, start the job, confirm process ownership, verify respawn on crash, and confirm logs/state land under the intended user home.
