# sources/sync-backup/syncthing/etc/freebsd-rc/syncthing

## Purpose
This shell script is a FreeBSD `rc.d` service template for running Syncthing as a daemon. It documents rc.conf knobs and starts Syncthing under a configured user with a pidfile and logfile.

## Important APIs, Types, And Functions
The script uses FreeBSD's `/etc/rc.subr` framework. It sets `name=syncthing`, `rcvar=syncthing_enable`, `start_cmd=syncthing_start`, and defines `syncthing_start` plus `syncthing_cleanup`. Configurable variables include `syncthing_enable`, `syncthing_home`, `syncthing_log_file`, `syncthing_user`, and `syncthing_group`. It invokes `/usr/sbin/daemon` with `-cf -p <pidfile> -u <user>`.

## Control Flow
After loading rc config, default variable values are assigned. The start function announces startup, creates and chowns the pidfile and logfile, then daemonizes `/usr/local/bin/syncthing serve` with `--home` and `--logfile` flags when configured. At the end, `run_rc_command $1` dispatches the requested rc action. `syncthing_cleanup` removes the pidfile if present, though the file does not explicitly wire it as a stop hook in the visible script.

## State And Persistence Behavior
The script creates `/var/run/syncthing.pid` and `/var/log/syncthing.log` by default. Configuration and runtime state are placed under `/usr/local/etc/syncthing` unless overridden. Ownership is set to the configured service user so the daemon can write its pid/log/config data.

## Dependencies And Integration Points
It integrates with FreeBSD rc service management, rc.conf, `/usr/sbin/daemon`, and the Syncthing CLI. The default binary path is `/usr/local/bin/syncthing`, matching FreeBSD package conventions. It maps service-level configuration into Syncthing's `serve` command and file-location flags.

## Risks And Edge Cases
Variable expansions are mostly unquoted in the daemon command and touch/chown lines, so paths with spaces or shell metacharacters are risky. The pidfile and logfile directories must already exist and be writable by root during service startup. The `syncthing_group` default is computed but not used in the start command. Because this is a template, the hard-coded defaults may need packaging-specific adjustments.

## Test Signals
Validation is mainly operational: install the rc script, set `syncthing_enable=YES`, run `service syncthing start`, and check pid/log/config ownership. Shell linting can catch quoting issues, but the meaningful signal is FreeBSD service startup and clean shutdown behavior.
