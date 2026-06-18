# File Research: sources/os/bsd/openbsd-src/sbin/shutdown/shutdown.c

This file implements OpenBSD `shutdown`: schedules system shutdown, broadcasts warnings, creates no-login/fastboot markers, runs shutdown scripts, and eventually halts, powers down, reboots, or signals init.

Key APIs:
- `main()`: verifies privilege, parses flags, unveils needed paths, pledges, parses time and message, daemonizes, and enters the warning loop.
- `getoffset()`: parses `now`, `+minutes`, `hhmm`, `hh:mm`, `yymmddhhmm`, and related absolute formats into `offset`.
- `loop()`: walks the warning interval table, broadcasts warnings, creates `/etc/nologin` near shutdown time, and calls final execution.
- `timewarn()`: forks `wall -n`, writes a formatted shutdown message, and limits wall runtime with `SIGALRM`.
- Final executor: logs the action, handles `-k`, creates `/fastboot` for `-f`, runs halt/reboot when requested, otherwise runs `/etc/rc shutdown` and signals init.
- `nolog()`, `doitfast()`, `finish()`, `timeout()`, `badtime()`, `usage()`: marker, cleanup, signal, and error helpers.

Behavior and integration:
- Supports `-d` dump, `-f` fast boot, `-h` halt, `-k` warn only, `-n` no sync, `-p` power down, `-r` reboot, and `-` to read warning text from stdin.
- Uses a restricted environment for `wall`.
- Creates `_PATH_NOLOGIN` five minutes before shutdown, unless interrupted cleanup removes it.
- For ordinary shutdown, revokes and reopens the console, runs `/etc/rc shutdown`, then sends `SIGTERM` to PID 1.

Risk notes:
- Time parsing mutates the input argument while normalizing `hh:mm`.
- Waiting for `wall` uses `wait(NULL)` and can observe unrelated children if any existed.
- The privileged execution path depends on exact `unveil()` and `pledge()` narrowing before final exec/script steps.
