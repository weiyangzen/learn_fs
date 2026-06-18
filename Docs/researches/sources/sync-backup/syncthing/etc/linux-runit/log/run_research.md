# sources/sync-backup/syncthing/etc/linux-runit/log/run

## Purpose
This short shell script is the runit log service for Syncthing. It receives stdout/stderr from the main runit service and forwards log lines to syslog via `logger`.

## Important APIs, Types, And Functions
The script consists of a POSIX shell shebang and `exec logger -t syncthing`. The `-t` tag marks syslog entries with `syncthing`.

## Control Flow
When runit starts the log service, the script immediately replaces the shell with `logger`. It reads from standard input as supplied by runit's logging pipeline and writes to the system logging facility.

## State And Persistence Behavior
The script itself persists no files. Persistence is delegated to the system logger configuration, which may write to journald, syslog files, or another backend depending on the distribution.

## Dependencies And Integration Points
It integrates with runit's paired service directory layout, where `etc/linux-runit/run` starts Syncthing and redirects stderr to stdout. It depends on a `logger` command compatible with `-t`.

## Risks And Edge Cases
If `logger` is unavailable or syslog is not running, runit log capture may fail. Because this script does not use `svlogd`, log retention and rotation are entirely outside this service directory. Very high log volume can stress syslog rather than a runit-managed log directory.

## Test Signals
Operational testing should start the runit service and confirm Syncthing output appears in syslog with the `syncthing` tag. Shell syntax is minimal and should be portable across `/bin/sh`.
