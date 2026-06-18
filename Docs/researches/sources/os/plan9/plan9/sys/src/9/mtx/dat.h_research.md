# File Research: sources/os/plan9/plan9/sys/src/9/mtx/dat.h

## Role

Machine-dependent data structure header for the MTX PowerPC Plan 9 port. It defines locks, labels, FPU state, memory configuration, MMU process state, machine state, ISA configuration, and global CPU/process registers.

This is kernel platform state, not filesystem logic.

## Main Contents

- Typedefs for core machine structures: `Conf`, `FPsave`, `Mach`, `Proc`, `Ureg`, `Vctl`, etc.
- `Lock`: includes key, saved status register, PC, owning proc/mach, and interrupt-lock flag.
- `Label`: stack and PC for context switching.
- FPU states: `FPinit`, `FPactive`, `FPinactive`, `FPillegal`.
- `FPsave`: 32 floating registers plus FPSCR.
- `Conf`/`Confmem`: memory and kernel sizing.
- `PMMU`: process MMU PID.
- Fake `kmap` macros for direct kernel mapping.
- `Mach`: per-CPU state including scheduler label, clocks, performance, MMU/TLB fields, and stack.
- `ISAConf`: parsed ISA configuration.
- `MACHP`, `mach0`, and register globals `m`/`up`.

## Important Behavior

- Includes shared `../port/portdat.h` after defining machine-dependent prerequisite structures.
- Defines Plan 9 AOUT magic as `Q_MAGIC`.
- `MACHP(n)` indexes CPUs by page-sized `Mach` areas.

## Dependencies And Assumptions

- Assembly in `mtx/l.s` depends on early `Mach` field offsets.
- Assumes PowerPC FPU save layout matches assembly `fpsave`/`fprestore`.

## Notable Risks

- Struct layout changes can break assembly.
- Fake `kmap` assumes direct physical-to-kernel address mapping.
