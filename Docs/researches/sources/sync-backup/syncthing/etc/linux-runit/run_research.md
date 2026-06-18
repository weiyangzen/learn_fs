# sources/sync-backup/syncthing/etc/linux-runit/run

## Purpose
This runit service script starts Syncthing under a configured non-root user. It is a simple template for systems using runit instead of systemd or other init systems.

## Important APIs, Types, And Functions
The script sets `USERNAME=jb`, `HOME="/home/$USERNAME"`, and `SYNCTHING="$HOME/bin/syncthing"`, then runs `exec 2>&1` followed by `exec chpst -u "$USERNAME" "$SYNCTHING" serve --logflags 0`. `chpst` is runit's privilege-change utility.

## Control Flow
On service start, the shell exports user-specific environment, redirects stderr to stdout for the paired log service, and replaces itself with Syncthing running as the configured user. Runit supervises the process and restarts according to service configuration.

## State And Persistence Behavior
Syncthing runs with `HOME=/home/jb` by default and therefore uses that user's normal config, database, and default folder locations unless the binary or config says otherwise. Logs go to stdout/stderr and then to the runit log service.

## Dependencies And Integration Points
It depends on runit, `chpst`, a real user named `jb` unless customized, and a Syncthing binary at `/home/jb/bin/syncthing`. It integrates with `etc/linux-runit/log/run` for logging and with Syncthing's `serve` command. `--logflags 0` adjusts Syncthing log formatting for supervisor-managed logs.

## Risks And Edge Cases
The template contains hard-coded example user and binary paths, so using it unmodified is likely wrong for packaged installs. If `HOME` and `USERNAME` diverge from system account metadata, Syncthing may read or write unexpected locations. There is no explicit `STNORESTART` or `--no-restart`; supervisor and Syncthing monitor behavior should be checked to avoid double supervision in a deployment.

## Test Signals
Functional validation is starting the runit service with customized variables and confirming the process runs as the intended user, logs through the paired logger, and restarts correctly under runit supervision.
