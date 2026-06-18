# File Research: sources/os/plan9/plan9/sys/src/9/port/devwd.c

Purpose: Watchdog framework device `#w/wdctl`. It registers a platform watchdog, optionally auto-starts it, lets users enable/disable/restart it, and disables it at shutdown.

Key logic:
- `addwatchdog` installs one global `Watchdog` and disables it initially.
- `wdinit` auto-enables the watchdog unless `*nowatchdog` is set.
- Auto-pet mode adds a clock callback that periodically calls `restart` while watchdog is on.
- Opening `wdctl` stops auto-petting and transfers control to user processes.
- Closing the final `wdctl` reference disables the watchdog.
- Reads call optional `wd->stat`; writes accept `enable`, `disable`, and `restart`.

Dependencies and integration:
- Uses platform `Watchdog` callbacks, `addclock0link`, `getconf`, Plan 9 device helpers, and exported `watchdog/watchdogon` globals for code that must pause long busy loops.

Risks and notes:
- Only one watchdog can be installed.
- User control disables automatic petting to avoid two independent owners.
