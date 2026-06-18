# File Research: sources/os/plan9/plan9/sys/src/9/omap/lproc.s

Small ARM process-transition assembly helpers.

Key responsibilities:
- `touser(SB)` performs the first transition from kernel to user mode, installing the user stack pointer in user `R13`, setting `SPSR` to user mode, pushing `UTZERO+0x20` as the initial PC, and returning through `RFE`.
- `forkret(SB)` restores a saved `Ureg` frame for a newly forked process and returns to user mode through `RFE`.

Important behavior:
- `touser` assumes the user entry point is always `UTZERO+0x20`.
- `forkret` mirrors the trap/syscall return frame layout produced in `lexception.s` and `syscall.c`.

Dependencies:
- Uses `mem.h`, `arm.h`, `UTZERO`, `PsrMusr`, and the expected ARM `Ureg` save layout.

Notable risks:
- These routines are tightly coupled to the assembly trap frame format; offsets are implicit.
