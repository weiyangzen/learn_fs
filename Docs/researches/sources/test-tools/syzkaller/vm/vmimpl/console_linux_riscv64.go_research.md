# sources/test-tools/syzkaller/vm/vmimpl/console_linux_riscv64.go

Purpose: Linux RISC-V 64 constants for serial console termios configuration.

Important APIs/types/functions: maps `unixCBAUD`, `unixCRTSCTS`, `syscallTCGETS`, and `syscallTCSETS` to `unix` package constants.

Control flow: no runtime behavior.

State and persistence: none.

Dependencies and integration: enables `OpenConsole` builds and runtime attempts on riscv64 Linux hosts.

Risks: no local behavioral tests; device/ioctl compatibility is discovered only at runtime.

Test signals: architecture build coverage and host-console integration.
