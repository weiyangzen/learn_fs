# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsco.c

Purpose: SCO Xenix/Unix and SVR4 console/framebuffer backend for Ghostscript PC framebuffer devices.

Key behavior:
- Opens the console device from `GSDEVICE` or defaults to `/dev/tty`.
- Provides non-GCC port output helpers using `CONSIO` ioctl.
- Installs signal handlers to restore video mode on interrupt/termination and exits on stop/continue signals rather than trying to resume graphics state.
- `pcfb_get_state` maps SCO console modes to BIOS-like display modes.
- `pcfb_set_mode` maps BIOS-like modes to SCO/SVR4 console mode ioctls, requests VGA I/O privilege when available, and maps console framebuffer memory via `MAPCONS`.
- `pcfb_set_state` restores the saved display mode.

Important dependencies:
- SCO/Xenix or SVR4 console headers and ioctls: `sys/console.h`, `sys/machdep.h`, `sys/kd.h`.
- Shared Ghostscript PC framebuffer API from `gdevpcfb.h`.

Notable risks / findings:
- Uses process-global console state and exits the process on many errors.
- Signal handling is intentionally crude for stop/continue cases.
