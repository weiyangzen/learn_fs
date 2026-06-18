# File Research: sources/os/plan9/9front/sys/src/9/teg2/dat.h

Tegra/ARM machine-dependent data definitions. It defines time constants, core typedefs, FP/VFP save structures, `Conf`, ARM MMU state in `Mach` and `Proc`, the `Mach` structure, fake kmap macros, global `active`, cache metadata, cache implementation interface, DMA mode enum, IRQ numbers, and the `Soc` address table structure.

`Mach` contains MMU fields known to assembly, fastclock state, probe/trap state, CPU frequency, VFP state, exception save areas, and stack. `PMMU` tracks L2 page-table pages. `Cacheimpl` provides the cache operation vtable used by drivers and MMU code.

The file also declares global cache pointers and platform globals such as `navailcpus`, `kseg0`, `memsize`, `l1ptstable`, and `machaddr`.
