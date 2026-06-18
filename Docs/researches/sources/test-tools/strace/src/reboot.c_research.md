# sources/test-tools/strace/src/reboot.c

Purpose: Decodes Linux `reboot` syscall magic constants and command values.

Important APIs/types/functions: `SYS_FUNC(reboot)`.

Control flow: prints magic1, magic2, command, and optional argument pointer/string according to command semantics, using xlat tables for known magic and reboot commands.

State and persistence: stateless.

Dependencies/integration: reboot xlat tables and standard syscall argument printers.

Risks: command-specific argument meaning is limited; unknown commands should retain raw values. Magic constants are part of user-visible output and golden tests are sensitive to xlat style.

Test signals: common reboot commands, unknown command values, raw/verbose xlat modes, and pointer argument cases.
