# sources/test-tools/syzkaller/vm/vmimpl/console_freebsd.go

Purpose: FreeBSD placeholder constants for shared console code.

Important APIs/types/functions: zero-valued `unixCBAUD`, `unixCRTSCTS`, `syscallTCGETS`, and `syscallTCSETS`.

Control flow: no runtime logic; it only satisfies symbols referenced by `console.go`.

State and persistence: none.

Dependencies and integration: no imports. It participates in cross-platform builds of `vmimpl`.

Risks: the comment says it is merely to fix build, so direct `OpenConsole` termios use on FreeBSD may not work correctly with zero ioctl request values.

Test signals: compile-only coverage; FreeBSD VM diagnosis is handled separately in `freebsd.go`.
