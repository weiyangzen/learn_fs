# File Research: sources/os/bsd/netbsd-src/sys/sys/wdog.h

Read completely: 109 lines.

Defines the user/kernel ioctl ABI for manipulating watchdog timers.

Core API:
- `WDOG_NAMESIZE` matches device `dv_xname` size.
- `struct wdog_mode` names a watchdog and carries mode plus period in seconds.
- `WDOGIOC_GMODE`, `SMODE`, `WHICH`, `TICKLE`, `GTICKLER`, and `GWDOGS` get/set modes, report the active watchdog, tickle user-tickle watchdogs, report last tickler PID, and enumerate watchdog names.
- `struct wdog_conf` points to a name buffer and count for enumeration.

Modes and features:
- Modes distinguish disarmed, kernel tickle, user tickle, and external tickle.
- Feature bit `WDOG_FEATURE_ALARM` requests audible alarm on expiry.
- `WDOG_PERIOD_DEFAULT` requests a default period; `WDOG_PERIOD_TO_TICKS` converts seconds to `hz` ticks.

Risks and notes:
- `WDOGIOC_GWDOGS` relies on caller-provided buffer sizing of `count * WDOG_NAMESIZE`.
- Only `UTICKLE` mode is tickled by the `TICKLE` ioctl according to the comments.
