# File Research: sources/os/plan9/9front/sys/src/9/kw/dat.h

Defines core machine data structures for the Kirkwood ARM port.

Key elements:
- Declares kernel architecture types such as `Conf`, `Mach`, `MMMU`, `PMMU`, `FPsave`, `Soc`, and `Memcache`.
- Defines process label layout and floating-point save state.
- Defines physical memory configuration and global system configuration fields.
- Defines per-machine state, including MMU, process pointer, exception stacks, fast clock, CPU type/revision, delay loop, and CPU frequency.
- Defines fake `kmap` helpers for this architecture.
- Defines ISA configuration parsing structure and device configuration structures.
- Defines cache description and SoC controller address layout.

Dependencies:
- Includes shared `portdat.h`.
- Referenced across the Kirkwood platform and generic kernel port code.

Research notes:
- The port assumes one cache color and uses a simple fake kmap model.
- Global `soc` is declared here and populated in `archkw.c`.
