# sources/test-tools/syzkaller/vm/vmimpl/console_netbsd.go

Purpose: NetBSD placeholder constants for shared console code.

Important APIs/types/functions: zero-valued `unixCBAUD`, `unixCRTSCTS`, `syscallTCGETS`, and `syscallTCSETS`.

Control flow: none.

State and persistence: none.

Dependencies and integration: compile-time integration with `console.go`.

Risks: marked as build-only; direct console termios setup is unlikely to be functional without real NetBSD ioctl values.

Test signals: build coverage only.
