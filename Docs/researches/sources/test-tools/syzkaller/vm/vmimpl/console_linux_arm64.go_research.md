# sources/test-tools/syzkaller/vm/vmimpl/console_linux_arm64.go

Purpose: Linux ARM64 constants for `vmimpl.OpenConsole`.

Important APIs/types/functions: provides `unixCBAUD`, `unixCRTSCTS`, `syscallTCGETS`, and `syscallTCSETS` from `golang.org/x/sys/unix`.

Control flow: no executable logic; selected by filename.

State and persistence: none.

Dependencies and integration: supports serial console access on ARM64 Linux hosts.

Risks: comment says compile-only confidence; host/device termios support remains the runtime risk.

Test signals: compile and platform integration coverage.
