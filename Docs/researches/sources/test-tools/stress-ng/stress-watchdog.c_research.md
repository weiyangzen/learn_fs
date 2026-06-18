# sources/test-tools/stress-ng/stress-watchdog.c

## Purpose
Implements Linux `watchdog`, a pathological OS stressor for `/dev/watchdog` open/close and watchdog ioctls while trying to avoid leaving a hardware watchdog armed.

## Important APIs, types, and functions
`stress_watchdog()` is the entry point when `linux/watchdog.h` exists. `stress_watchdog_magic_close()` writes `"V"` to disable supporting watchdogs. `stress_watchdog_handler()` magic-closes on many signals and clears the continue flag. The loop uses `open()`, `close()`, and `ioctl()` for keepalive, timeout, pretimeout, timeleft, support, status, bootstatus, and temperature.

## Control flow
The stressor installs signal handlers, checks `/dev/watchdog` access, skips successfully if absent/inaccessible, synchronizes, and loops opening the device. On success it writes magic close, issues supported ioctls, validates nonnegative returned values, writes magic close again, closes, yields, and increments bogo. If the device is busy, it nanosleeps and retries.

## State and persistence
Global `fd` is shared with signal handlers. The kernel watchdog device may have persistent hardware effects, but the code writes magic close and closes descriptors; no repo files are written.

## Dependencies and integration points
Registered as `stress_watchdog_info` with `CLASS_OS | CLASS_PATHOLOGICAL` and `VERIFY_ALWAYS`. Depends on Linux watchdog UAPI and stress-ng signal helpers. Without headers, it is unimplemented.

## Risks and edge cases
Real watchdog devices can reboot the system if left armed. Magic close is driver-dependent, and crashes between open/close remain risky. Multiple instances contend for an exclusive device. Negative timeout or temperature values are treated as verification failures.

## Test signals
Bogo increments show completed open/ioctl/close cycles. Missing or inaccessible `/dev/watchdog` is a successful skip. Failures include invalid negative ioctl values and close errors.
