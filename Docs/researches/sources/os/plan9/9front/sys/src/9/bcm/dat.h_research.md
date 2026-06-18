# File Research: sources/os/plan9/9front/sys/src/9/bcm/dat.h

BCM/ARM kernel data structure definitions.

Key definitions:
- Time constants and architecture typedefs.
- FPU save/allocation structures supporting hardware VFP and software emulation.
- `Conf`/`Confmem`, Mach MMU state, and process MMU state.
- `Mach` layout with assembly-known fields, CPU timing, FPU state, and exception-mode scratch save areas.
- Fake `KMap` macros for direct mapping.
- Global active CPU state, register-bound `m`/`up`, and `machaddr`.
- `ISAConf`, debug macros, device descriptors, SoC descriptor, and GPIO function constants.

Dependencies:
- Includes `../port/portdat.h`.

Research notes:
- `m` is register `R10` and `up` is `R9` on this port.
- The `Soc` structure drives bus/physical/virtual address translation across DMA and device code.
