# File Research: sources/os/plan9/plan9/sys/src/cmd/va/l.s

MIPS kernel low-level assembly support file.

Contents:
- Memory, timing, CP0 register, status bit, trap, segment, PTE, and address-space constants.
- `start` bootstrap for the first processor: sets status/FPU, clears BSS, records argc/argv/env, and calls `main`.
- `touser` transitions to user mode with a supplied stack pointer.
- `newstart` brings secondary processors online.
- Firmware jump helper.
- Interrupt priority functions: `splhi`, `spllo`, `splx`.
- Write-buffer flush, label save/restore, and `gotopc`.
- TLB helpers: put/probe/read entries and indexed TLB writes.
- Exception vector and `exception` handler path for user/kernel traps and syscalls.
- Register save/restore helpers for general registers and floating-point registers.
- `rfnote` restore path.
- Instruction and data cache flush routines.

This is machine/runtime support, not assembler implementation. It is included in this group because it lives under `cmd/va`.
