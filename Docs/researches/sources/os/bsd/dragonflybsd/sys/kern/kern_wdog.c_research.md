# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_wdog.c

Implements kernel watchdog registration, periodic reset, sysctl control, and `/dev/wdog` ioctl reset support.

Key state:
- `wdoglist`: registered watchdog devices.
- `wdogmtx`: spinlock protecting list and periods.
- `wdog_callout`: automatic reset callout.
- `wdog_auto_enable`: whether kernel auto-reset is enabled.
- `wdog_auto_period`: current/minimum period.

Key APIs:
- `wdog_register()`
- `wdog_unregister()`
- `wdog_disable()`
- `wdog_ioctl()`

Important behavior:
- `wdog_register()` initializes device period, inserts into list, immediately resets all watchdogs, and logs registration.
- `wdog_unregister()` removes a watchdog and logs.
- `wdog_reset_all()` calls each watchdog’s callback, tracks the minimum returned period, and if auto mode is enabled schedules the next reset at half that minimum period.
- `wdog_set_period()` applies a period to all registered watchdogs.
- `kern.watchdog.auto` sysctl toggles automatic reset and starts/stops the callout behavior.
- `kern.watchdog.period` sysctl adjusts all watchdog periods and triggers reset.
- `wdog_disable()` stops auto callout, sets all periods to zero, and resets all watchdogs.
- `/dev/wdog` accepts `WDIOCRESET` only when auto mode is disabled.
- `wdog_init()` creates `/dev/wdog`, initializes spinlock and callout.
- `wdog_uninit()` cancels/terminates callout and removes device ops.

Concurrency model:
- Spinlock protects watchdog list and period updates.
- Callout is initialized MP-safe.

Filesystem relevance:
- Creates a character device node through devfs. Not a filesystem implementation, but its device-node lifecycle and ioctl behavior are visible through the filesystem namespace.
