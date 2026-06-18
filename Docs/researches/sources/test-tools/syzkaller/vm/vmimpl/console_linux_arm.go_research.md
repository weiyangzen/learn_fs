# sources/test-tools/syzkaller/vm/vmimpl/console_linux_arm.go

Purpose: Linux ARM constants for shared console setup.

Important APIs/types/functions: maps `unixCBAUD`, `unixCRTSCTS`, `syscallTCGETS`, and `syscallTCSETS` to `unix.CBAUD`, `unix.CRTSCTS`, `unix.TCGETS2`, and `unix.TCSETS2`.

Control flow: compile-time constants only.

State and persistence: none.

Dependencies and integration: feeds `OpenConsole` on ARM Linux hosts.

Risks: file comment notes it compiles but was not tested; unsupported ioctl behavior appears as console-open failure.

Test signals: build coverage and any ARM host serial-console integration run.
