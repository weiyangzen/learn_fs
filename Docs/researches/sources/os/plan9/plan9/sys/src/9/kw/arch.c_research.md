# File Research: sources/os/plan9/plan9/sys/src/9/kw/arch.c

## Purpose
Provides ARM architecture glue for the Kirkwood Plan 9 kernel: process register setup, user/kernel accounting on exit, alignment validation, kproc bootstrap, process save/restore hooks, user-mode detection, and simple atomic operations.

## Main Functions
- `setkernur`: fabricates enough `Ureg` context to show a sleeping kernel process stack.
- `validalign`: validates user address alignment, relaxing 64-bit alignment to 32-bit on this 32-bit ARM port.
- `kexit`: updates user-visible `Tos` cycle accounting before returning to user mode and flushes the cache line to make it visible.
- `userpc`, `dbgpc`, `userureg`: inspect saved user register state.
- `kprocchild` and `linkproc`: set initial stack/PC and run the kernel-process function.
- `procsetup`, `procsave`, `procrestore`: delegate FPU process hooks and maintain process cycle accounting.
- `_xinc`, `_xdec`, `ainc`, `adec`, `cas32`: interrupt-masked atomic primitives with coherence after successful CAS.

## Dependencies and Integration
Depends on ARM `Ureg`, `Proc`, scheduler labels, `Tos`, FPU helpers, interrupt priority primitives, and cache maintenance.

## Risks and Notes
The atomic operations are coarse-grained, implemented by raising interrupt priority rather than hardware atomic instructions. `setregisters` is a placeholder and deliberately does not allow devproc register modification here.
