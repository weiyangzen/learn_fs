# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/watchdog.c

Plan 9 watchdog feeder utility.

Key behavior:
- Opens watchdog control device `#w/wdctl`.
- Forks into background using `rfork(RFPROC|RFNOWAIT|RFFDG)` and exits parent.
- Raises child process priority by writing `pri 18` to `/proc/<pid>/ctl`.
- Writes `enable` to watchdog device, then loops forever:
  - sleeps 300 ms,
  - seeks to start,
  - writes `restart`.

Important details:
- Designed around a watchdog timeout and CPU-speed comment: “allows 4.2GHz CPU, with some slop”.
- Uses `sysfatal` on failures.

Filesystem relevance:
- Direct Plan 9 namespace/device-file interaction with `/proc` and `#w`, but not filesystem implementation logic.
