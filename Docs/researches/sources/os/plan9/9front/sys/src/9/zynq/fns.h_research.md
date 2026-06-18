# File Research: sources/os/plan9/9front/sys/src/9/zynq/fns.h

Purpose: Zynq platform function declarations and machine macros.

Key interfaces:
- Address helpers: `kaddr`, `paddr`, `cankaddr`, `KADDR`, `PADDR`.
- Process/MMU/cache functions: `procsave`, `procrestore`, `kmap`, `kunmap`, `mmuinit`, `ttbget/put`, `vmap`, `tmpmap`, `flushpg`, `setasid`, `flushtlb`.
- Interrupt/timer/device init declarations.
- ARM cache maintenance and DMA helpers.
- Screen, architecture, and config declarations.

Integration notes: Includes `../port/portfns.h` and is consumed by most Zynq C files.

Risk/attention points: Header must match assembly exports in `l.s`; mismatches would fail at link time or cause ABI bugs.
