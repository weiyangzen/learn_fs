# sources/test-tools/syzkaller/vm/vmimpl/console_darwin.go

Purpose: Darwin-specific terminal ioctl constants used by `console.go`.

Important APIs/types/functions: constants `unixCBAUD`, `unixCRTSCTS`, `syscallTCGETS`, and `syscallTCSETS`; the latter two map to `syscall.TIOCGETA` and `syscall.TIOCSETA`.

Control flow: no runtime logic. The file supplies compile-time constants selected by Go build constraints through filename suffix.

State and persistence: none.

Dependencies and integration: imports `syscall` and integrates with `OpenConsole` termios get/set calls.

Risks: baud and flow-control masks are zero on Darwin, so Linux-style bit clearing is intentionally inert; real serial behavior depends on Darwin termios compatibility.

Test signals: build coverage on Darwin is the main signal; no direct unit test is assigned.
