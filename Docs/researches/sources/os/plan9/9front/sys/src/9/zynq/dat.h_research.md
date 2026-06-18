# File Research: sources/os/plan9/9front/sys/src/9/zynq/dat.h

Purpose: Zynq ARM kernel machine data definitions for 9front.

Key interfaces:
- Core typedef declarations for kernel structs.
- `Label`, `FPsave`, `PFPU`, `Confmem`, `Conf`, `PMMU`, `L1`, `MMMU`, `Mach`, `ISAConf`, `DevConf`.
- FPU states and `NCOLOR`.
- Global `active`, register variables `m` and `up`, and MMIO globals `mpcore`, `slcr`.

Integration notes: Includes `../port/portdat.h`, so it anchors platform-specific structures before portable kernel data.

Risk/attention points: `Mach` layout has an “end of known to assembly” boundary; assembly files depend on early field offsets.
