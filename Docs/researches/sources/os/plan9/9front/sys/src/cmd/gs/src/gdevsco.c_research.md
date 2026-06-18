# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsco.c

SCO Xenix/Unix and AT&T SVR4 console framebuffer support for Ghostscript PC framebuffer devices.

Key behavior:
- Opens the console device named by `GSDEVICE`, defaulting to `/dev/tty`.
- Provides non-GCC port output helpers using `CONSIO` ioctl calls for register writes.
- Installs signal handlers so interrupts or termination restore the video mode before exiting.
- Handles suspend/continue signals conservatively by exiting through the interrupt handler in the enabled code path.
- Reads the current console display mode with `CONS_CURRENT` and maps it to PC framebuffer mode identifiers.
- Sets VGA/EGA text or graphics modes through SCO/SVR4 console ioctls.
- Maps display memory with `MAPCONS` and stores the framebuffer address in global `fb_addr`.
- Restores saved video state by resetting the saved display mode.

Notable dependencies:
- Ghostscript PC framebuffer layer: `gdevpcfb.h`.
- SCO/Xenix/SVR4 console headers and ioctls: `sys/console.h`, `sys/machdep.h`, `sys/kd.h`, `CONSIO`, `MAPCONS`, `VGA_IOPRIVL`.

Research notes:
- This is an OS adapter for direct console graphics access.
- Error paths often call `ega_close`, print diagnostics, and terminate the process.
- The code is platform-specific and not related to filesystem behavior.
