# File Research: sources/os/plan9/plan9/sys/src/9/ppc/dat.h

## Role

PPC machine-dependent core type and structure definitions used before and alongside `portdat.h`.

## Main Definitions

Defines architecture versions of `Lock`, `Label`, floating-point save state, memory configuration (`Confmem`, `Conf`), process MMU state (`PMMU`), notification save state, fake `KMap`, and the PPC `Mach` structure. `Mach` includes fields known by assembly for processor id, current proc, TLB miss counters, plus clocks, MMU state, scheduler state, performance, interrupt stats, and stack.

Also defines global `active` state, `ISAConf` parsed configuration entries, interrupt vector control `Vctl`, and externs for `mach0`, register globals `m` and `up`, and `initfp`.

## Dependencies

Included by most PPC kernel sources. Must stay consistent with assembly offsets in `l.s`, FP save/restore routines, and shared `../port/portdat.h`.

## Risks

Layout changes can break assembly. `active` is defined in this header, so include discipline matters. Fake kmap macros assume direct kernel mapping via `KZERO`.
