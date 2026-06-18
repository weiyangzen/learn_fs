# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/termios.h

## Purpose
Defines the POSIX and extended illumos terminal control ABI: `struct termios`, terminal flag types, control character indexes/defaults, input/output/control/local mode bits, ioctl numbers, speed constants, PPS event structures, and window-size structure.

## Main Interfaces
- Types:
  - `tcflag_t`
  - `cc_t`
  - `speed_t`
  - `struct termios`
- Userland APIs:
  - speed get/set helpers
  - `tcgetattr()`, `tcsetattr()`
  - `tcsendbreak()`, `tcdrain()`, `tcflush()`, `tcflow()`
  - `tcgetsid()` where exposed
- Control character indexes and defaults:
  - `VINTR`, `VQUIT`, `VERASE`, `VKILL`, `VEOF`, `VEOL`, `VMIN`, `VTIME`, `VSTART`, `VSTOP`, `VSUSP`, and extended indexes/defaults.
- Mode bit families:
  - input flags such as break/parity/CR/NL/flow-control handling
  - output flags and delay masks
  - control flags for character size, parity, hangup, local mode, hardware flow control, baud extension bits
  - local flags for signal/canonical/echo/job-control behavior
- Ioctl constants:
  - System V `TCGETA`/`TCSETA*`
  - POSIX `TCGETS`/`TCSETS*`
  - BSD/job-control/modem/pty compatibility ioctls
  - PPS ioctls and `struct ppsclockev`
- Speed constants from `B0` through `B4000000`.
- `struct winsize`.

## Dependencies And Relationships
Includes feature-test, tty device/time extensions, and types headers depending on standards exposure macros. Used by libc, terminal drivers, STREAMS modules, ptys, and compatibility layers.

## Research Notes
Large parts of the header are gated by `__XOPEN_OR_POSIX`, `_POSIX_C_SOURCE`, `_XPG6`, and `__EXTENSIONS__` to preserve standards visibility rules while still exposing illumos/BSD/System V extensions when requested.
