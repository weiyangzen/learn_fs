# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/reboot.c

Watchdog-style reboot helper. It monitors a file or CPU-library path and reboots if a stat request fails for reasons other than timeout/alarm.

Core behavior:
- If an argument is supplied, monitors that path.
- Otherwise reads `/env/cputype` and monitors `/<cputype>/lib`.
- Forks into the background.
- Opens the monitored path and every five minutes attempts `dirfstat()`, with a one-minute alarm.
- If `dirfstat()` fails without alarm interruption, writes `reboot` to `/dev/reboot`.

Important functions:
- `readenv()` reads `/env/name`.
- `ding()` converts alarm notes into continuable interruptions.
- `reboot()` writes to `/dev/reboot`.

Dependencies and integration:
- Standalone Plan 9 libc command.
- Depends on `/dev/reboot`, `/proc` note/alarm behavior, and namespace file availability.

Notable risks:
- Reboots on non-alarm stat failure, so namespace/server transient errors can become machine resets.
- Does not log failures before reboot.
