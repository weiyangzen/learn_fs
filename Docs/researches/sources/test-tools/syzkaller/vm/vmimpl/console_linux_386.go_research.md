# sources/test-tools/syzkaller/vm/vmimpl/console_linux_386.go

Purpose: Linux 386 constants for shared serial-console termios setup.

Important APIs/types/functions: maps `unixCBAUD`, `unixCRTSCTS`, `syscallTCGETS`, and `syscallTCSETS` to `golang.org/x/sys/unix` constants, using `TCGETS2`/`TCSETS2`.

Control flow: no runtime logic. The file is selected by architecture-specific filename.

State and persistence: none.

Dependencies and integration: imported by build selection into the `vmimpl` package so `OpenConsole` can set baud, character size, parity, stop bits, and hardware flow control.

Risks: comment notes it builds but is not tested; ioctl support can vary by device/host kernel.

Test signals: compile and any host-side serial console use on linux/386.
