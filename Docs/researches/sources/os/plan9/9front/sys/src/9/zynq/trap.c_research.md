# File Research: sources/os/plan9/9front/sys/src/9/zynq/trap.c

Implements ARM/Zynq kernel trap, syscall, notification, and floating-point context handling for the 9front kernel.

Key responsibilities:
- Handles undefined-instruction, instruction-abort, data-abort, and IRQ traps in `trap`.
- Converts ARM fault status/address information into kernel panics or user notes via `faultarm`.
- Lazily allocates, saves, restores, and clears per-process FP state through `mathtrap`, `fpunotify`, `fpunoted`, `notefpsave`, `procsave`, `procfork`, and `procsetup`.
- Builds user notification frames in `notify` and validates/restores user register state in `noted`.
- Provides debug support through `_dumpstack`, `dumpstack`, `dumpregs`, `userpc`, and `dbgpc`.
- Sets up fork/exec/kernel-child register state with `setkernur`, `forkchild`, `kprocchild`, and `execregs`.

Important dependencies:
- Uses Plan 9 kernel globals `m` and `up`, ARM fault helpers `getifsr/getifar/getdfsr/getdfar`, scheduler hooks, note delivery, and MMU switching via `l1switch`.
- Stack dumping emits `ktrace /arm/9zynq` input for postmortem analysis.

Notable details:
- Kernel faults on addresses above `USTKTOP` panic immediately.
- FP notify handling preserves an old FP save area in `ofpsave` so note handlers can run without losing interrupted FP state.
