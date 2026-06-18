# sources/test-tools/syzkaller/vm/vmimpl/console_linux_amd64.go

Purpose: Linux AMD64 constants for `OpenConsole` termios manipulation.

Important APIs/types/functions: maps baud and flow-control masks plus `TCGETS2`/`TCSETS2` ioctl request constants from `golang.org/x/sys/unix`.

Control flow: no functions; build-system filename selection supplies constants.

State and persistence: none.

Dependencies and integration: used by `console.go` on common Linux hosts, including syzkaller development and CI environments.

Risks: assumes `TCGETS2`/`TCSETS2` are appropriate for the opened console device. Errors propagate from `OpenConsole` if unsupported.

Test signals: indirect coverage from Linux backend runs that open physical or emulated serial consoles.
