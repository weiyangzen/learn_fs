# File Research: sources/os/plan9/plan9/sys/src/9/rb/dat.h

RouterBOARD/MIPS machine data definitions shared with the Plan 9 port layer.

Key contents:
- Type forwards for kernel machine objects and `Tval`.
- MIPS boot magic definitions.
- Machine-specific `Lock`, `Label`, `Confmem`, and `Conf` structures.
- Emulated FP state definitions and `FPsave` structure, including raw 32-bit FP registers, FCR31, branch-delay emulation state, and stuck-fault tracking.
- Per-process PMMU state.
- `Mach` layout, with first fields explicitly fixed for `l.s`.
- `KMap` and software TLB entry structures.
- Active-machine global and external register variables `m` and `up`.

Role:
- Defines the ABI between MIPS assembly, MMU/fault code, process code, FP emulator, and the generic Plan 9 port layer.

Notable risks:
- `Mach` first-member ordering is hard-coded in assembly.
- FP emulation state is exposed through `/dev/proc` expectations by keeping registers first.
