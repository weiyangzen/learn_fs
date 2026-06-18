# sources/test-tools/syzkaller/vm/vmimpl/console_linux_s390x.go

Purpose: Linux s390x constants for the common console opener.

Important APIs/types/functions: defines baud mask, hardware flow-control mask, and `TCGETS2`/`TCSETS2` constants from `golang.org/x/sys/unix`.

Control flow: constants only.

State and persistence: none.

Dependencies and integration: supports `OpenConsole` on s390x Linux builds.

Risks: lacks direct tests; the termios2 ioctl path may not match all console devices.

Test signals: compile and platform integration runs.
