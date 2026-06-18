# File Research: sources/os/plan9/plan9/sys/src/9/pc/plan9l.s

Small x86 assembly helpers for entering user mode and optimized syscall interrupt dispatch.

Key elements:
- Defines `touser`: constructs an interrupt-return frame with user data/code selectors, user stack, IF flag, and PC `UTZERO+32`, loads user segment registers, and executes `IRETL`.
- Defines `_syscallintr`: fast syscall vector handler that saves segment/general registers, switches DS/ES to kernel selectors, calls `syscall`, restores registers, removes trap metadata, and returns via `IRETL`.

Interactions:
- Must match syscall vector `0x40` from `io.h`.
- Complements trap/syscall handling in lower-level PC assembly and kernel trap code.

Research notes:
- Process/user transition substrate only.
