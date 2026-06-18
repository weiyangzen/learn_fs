# File Research: sources/os/bsd/freebsd-src/sbin/shutdown/shutdown.c

## Summary
Implements the FreeBSD `shutdown` and `poweroff` command. It parses shutdown time and mode, broadcasts warnings, creates/removes the no-login file, logs the action, and signals init or execs halt/reboot paths.

## Main Responsibilities
- Requires effective root outside `DEBUG`.
- Treats invocation as `poweroff` as `shutdown -p now`.
- Parses shutdown modes: single-user, reboot, halt, poweroff, power-cycle, fake shutdown, fast exec path, no-sync fast path, quiet warning suppression, and ignore-noshutdown.
- Parses time formats: `now`, `+N` with seconds/minutes/hours suffixes, `hhmm`, `hh:mm`, `ddhhmm`, `mmddhhmm`, and `yymmddhhmm`.
- Builds optional warning messages from argv or stdin.
- Refuses shutdown when `_PATH_NOSHUTDOWN` exists unless forced.
- Forks into background, raises priority, starts a new session, and uses syslog.
- Broadcasts warning messages through `wall -n`.
- Creates `_PATH_NOLOGIN` during the final five minutes.
- Signals init for normal shutdown paths or execs `reboot`/`halt` for `-o`.

## Key Elements
- `getoffset()`: shutdown time parser.
- `loop()`: warning/sleep schedule.
- `timewarn()`: `wall` broadcast writer with restricted environment.
- `nolog()`: writes no-login file with shutdown time and message.
- `finish()`: cleanup on termination.
- Final action routine: logs and triggers init signals or fast halt/reboot executables.

## Dependencies And Integration
Uses init signal conventions, `/etc/nologin` path macros, `wall`, `halt`, `reboot`, syslog, boottrace, passwd lookup, and standard daemonization primitives.

## Research Notes
The `-o -n` path bypasses init and can pass no-sync to `halt`/`reboot`; argument validation prevents `-n` without `-o` and requires `-o` to be paired with a terminal power/reboot mode.
