# sources/test-tools/syzkaller/vm/vmimpl/console_openbsd.go

Purpose: OpenBSD placeholder constants for shared console code.

Important APIs/types/functions: zero-valued termios masks and ioctl constants.

Control flow: no executable logic.

State and persistence: none.

Dependencies and integration: keeps `vmimpl` compiling on OpenBSD-related builds; OpenBSD VM diagnosis itself is in `openbsd.go`.

Risks: direct `OpenConsole` use is build-satisfied but not behaviorally implemented.

Test signals: compile-only coverage.
