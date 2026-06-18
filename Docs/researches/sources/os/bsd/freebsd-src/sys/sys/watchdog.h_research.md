# File Research: sources/os/bsd/freebsd-src/sys/sys/watchdog.h

Public and kernel watchdog control interface.

Key content:
- Defines watchdog device path component `_PATH_WATCHDOG` as `"fido"`.
- Defines ioctl commands for patting the watchdog, setting/getting timeout, getting remaining time, setting/getting pre-timeout, selecting pre-timeout action, selecting software watchdog mode, configuring software timeout action, and generic watchdog control.
- Defines mode/control bits: `WD_ACTIVE`, `WD_PASSIVE`, `WD_LASTVAL`, `WD_INTERVAL`, and `WD_CTRL_DISABLE`/`ENABLE`/`RESET`.
- Defines human-oriented timeout exponent constants from never through 1 ms, 125 ms, 250 ms, 500 ms, 1 sec, and up to 128 sec.
- Defines pre-timeout software actions: panic, enter debugger, log, printf, and mask.
- Kernel section declares watchdog eventhandler callback types, eventhandler lists, kernel pat/control helpers for integer and `sbintime_t` timeouts, and the `wdog_software_attach` hook.

Research relevance:
- Shows FreeBSD’s watchdog ABI as a small ioctl/eventhandler contract.
- Relevant to OS substrate research rather than VFS, but it illustrates how kernel services expose both user-control and eventhandler-backed device/provider interfaces.
