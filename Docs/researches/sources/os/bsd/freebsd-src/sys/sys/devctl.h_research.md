# File Research: sources/os/bsd/freebsd-src/sys/sys/devctl.h

## Purpose
Declares kernel devctl event notification hooks.

## Main Elements
- `devctl_process_running()` reports whether the devctl consumer process is active.
- `devctl_notify()` sends system/subsystem/type/data events.
- `devctl_safe_quote_sb()` quotes strings into an sbuf.
- Hook type `send_event_f` and setters install or remove notification hooks.

## Dependencies And Integration
Kernel-only header used by device, devfs, bus, and subsystem code that emits devctl events.

## Risk Notes
Event payload strings are externally visible. Callers should quote and format data carefully to avoid ambiguous or unsafe devd input.
