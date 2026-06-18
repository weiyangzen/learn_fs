# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_reboot.c

## Purpose

`kern_reboot.c` implements the machine-independent reboot/shutdown syscall wrapper and shared reboot entry point.

## Main Responsibilities

- `kern_reboot(int howto, char *bootstr)`
  - Serializes reboot attempts using an atomic compare-and-swap on a static `rebooter` LWP pointer.
  - If another LWP is already rebooting, waits in `kpause("reboot", ...)`.
  - Sets `shutting_down = 1`.
  - If the kernel is cold, jumps directly to `cpu_reboot()`.
  - If syncing is allowed and not panicking, writes adjusted time back to TODR when `time_adjusted != 0`.
  - Delegates machine-dependent final work to `cpu_reboot(howto, bootstr)`.
- `sys_reboot()`
  - Requires `KAUTH_SYSTEM_REBOOT`.
  - Copies an optional boot string only when `RB_STRING` is set.
  - Calls `kern_reboot()`.

## Notes

The file intentionally leaves most shutdown details to per-port `cpu_reboot()`, with a comment noting that common reboot behavior could be refactored into this MI layer.
