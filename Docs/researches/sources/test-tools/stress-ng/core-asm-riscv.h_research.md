# sources/test-tools/stress-ng/core-asm-riscv.h

Purpose: RISC-V inline wrappers for time, fences, pause, cache block operations, and Linux hardware probing.

Important APIs and control flow: defines CBO instruction encoding helpers, `rdtime`, `fence`, `fence.i`, encoded pause, optional `cbo.zero/flush/clean`, and Linux `riscv_hwprobe` helpers for Zicbom support and cache block size.

State and persistence: no persistent state; `riscv_hwprobe` reads kernel/hardware feature state and uses current affinity mask.

Dependencies and integration: depends on RISC-V architecture macros, optional `<asm/hwprobe.h>`, `syscall`, `sched_getaffinity`, and generated assembler macros.

Risks and test signals: manually encoded instructions must track ISA encoding and endian handling; hwprobe availability varies by kernel. Signals are RISC-V builds and feature-gated stressor behavior.
