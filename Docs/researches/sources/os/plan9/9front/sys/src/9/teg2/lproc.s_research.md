# File Research: sources/os/plan9/9front/sys/src/9/teg2/lproc.s

Small ARM process-transition assembly.

Purpose:
- Implements the first jump from kernel to user mode and fork return.

Key behavior:
- `touser` installs the user stack pointer into banked user SP, builds a user-mode return frame, and returns to `UTZERO+0x20` with `RFEV7W`.
- `forkret` adjusts from saved process trap frame layout and branches to `rfue` to resume the child process.

Integration:
- Called by `init0()` in `main.c` and by scheduler/fork setup in common kernel code.
- Shares `Ureg` stack-frame conventions with `lexception.s` and `trap.c`.

Risks/notes:
- Extremely layout-sensitive; any `Ureg` or stack convention change must be reflected here.
