# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/wait.h

`wait.h` defines process-wait option flags, wait-status decoding macros, and userland wait-family prototypes. It is gated by feature-test macros to expose POSIX/XPG/extension interfaces with the correct namespace.

Always-visible wait options include `WUNTRACED` and `WNOHANG`. Under broader X/Open or extension exposure, the header adds `WEXITED`, `WTRAPPED`, `WSTOPPED`, `WCONTINUED`, `WNOWAIT`, and `WOPTMASK`. Status helper constants and macros expose low/high-byte decoding, stopped/continued/core-dump tests, and signal/exit status extraction.

The standard wait status macros use the traditional encoded integer layout: low byte zero means exited, low byte nonzero with no high-byte data means signaled, low byte `0177` with high-byte data means stopped, and `0177777` represents continued state.

Outside `_KERNEL`, the header declares `wait()`, `waitpid()`, and, when permitted by feature tests, `waitid()`, legacy `wait3()`, and extension `wait4()`. It includes `resource.h`, `siginfo.h`, and `procset.h` only when those declarations are needed.
