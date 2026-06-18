# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_watchdog.c

Read completely: 108 lines.

Implements the generic kernel watchdog control shim. Hardware drivers register a callback, and `KERN_WATCHDOG` sysctls control watchdog period and automatic tickling.

Core state:
- `wdog_ctl_cb` and `wdog_ctl_cb_arg` hold the registered hardware control callback and argument.
- `wdog_period` stores the active period in seconds.
- `wdog_auto` controls whether the kernel periodically refreshes the watchdog.
- `wdog_timeout` is the timeout used for automatic half-period tickles.

Behavior:
- `wdog_register()` accepts the first watchdog provider only and initializes `wdog_timeout`.
- `wdog_tickle()` calls the registered provider with the current period and reschedules itself for half the period in milliseconds.
- `wdog_shutdown()` cancels the timeout, disables the hardware watchdog by calling the provider with period 0, clears the callback, and restores defaults when the caller's argument matches.
- `sysctl_wdog()` exposes `KERN_WATCHDOG_PERIOD` and `KERN_WATCHDOG_AUTO`, using `sysctl_int_bounded()`. Period writes stop any current timeout, call the provider, and store the provider-returned period.

Concurrency and dependencies:
- Uses the timeout subsystem for recurring tickles.
- Returns `EOPNOTSUPP` if no watchdog provider is registered.
- No explicit mutex is used here; callers rely on the surrounding sysctl path and simple single-provider semantics.
