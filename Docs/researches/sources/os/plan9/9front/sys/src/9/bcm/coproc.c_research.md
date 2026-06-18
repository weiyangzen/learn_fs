# File Research: sources/os/plan9/9front/sys/src/9/bcm/coproc.c

Dynamic ARM coprocessor and VFP register access thunk generator.

Key behavior:
- Emits small executable instruction pairs for arbitrary MRC/MCR and VFP control/register operations.
- Caches generated instruction stubs per CPU.
- Provides generic `cprd/cpwr`, CP15 convenience wrappers, VFP control `fprd/fpwr`, and VFP data register save/restore helpers.
- Flushes data/instruction caches after emitting new instructions.

Dependencies:
- Uses cache maintenance, locking, ARM coprocessor constants, and per-CPU `m`.

Research notes:
- Mirrors ARM64 `sysreg.c` for the ARMv6/v7 coprocessor encoding model.
