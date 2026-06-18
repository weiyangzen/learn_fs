# File Research: sources/os/plan9/9front/sys/src/9/omap/coproc.c

Runtime helpers for ARM coprocessor and VFP register access.

Key behavior:
- `cpwr` and `cprd` synthesize small instruction sequences containing MCR/MRC and a return instruction, flush caches, then execute them.
- `cpwrsc` and `cprdsc` specialize access to CP15 system-control registers.
- `fprd` and `fpwr` synthesize VMRS/VMSR sequences for VFP system register access.
- `MAP2PCSPACE` maps generated stack instructions into the caller PC segment before execution.

Research notes:
- The generated-code approach avoids needing static assembly wrappers for every CP15/VFP register tuple.
- Correctness depends on cleaning data cache and invalidating instruction cache before calling generated code.
