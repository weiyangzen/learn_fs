# File Research: sources/os/plan9/plan9/sys/src/9/kw/l.s

## Role

Core ARM assembly for the Kirkwood kernel: reset/startup, first page-table construction, cache and MMU control, coprocessor register access, interrupt priority primitives, atomic operations, labels, idle, and memory barriers.

This is low-level kernel architecture support, not filesystem code.

## Main Interfaces

- Boot/reset:
  - `_start`
  - `_reset`
  - `_r15warp`
  - `myputc`
- Cache control:
  - `l1cacheson`, `l1cachesoff`
  - `cachedwb`, `cachedwbse`
  - `cachedwbinv`, `cachedwbinvse`
  - `cachedinv`, `cachedinvse`
  - `cacheuwbinv`, `cacheiinv`
  - `l2cachecfgon`, `l2cachecfgoff`
  - `l2cacheuwb`, `l2cacheuwbse`, `l2cacheuwbinv`, `l2cacheuwbinvse`
  - `l2cacheuinv`, `l2cacheuinvse`
- MMU/register access:
  - `mmuenable`, `mmudisable`
  - `mmuinvalidate`, `mmuinvalidateaddr`
  - `cpidget`, `cpctget`, `controlget`, `ttbget`, `ttbput`
  - `dacget`, `dacput`, `fsrget`, `farget`, `pidget`, `pidput`
- Interrupt priority:
  - `splhi`, `spllo`, `splx`, `splxpc`, `spldone`, `islo`, `splfhi`
- Atomics/control:
  - `tas`, `_tas`, `clz`, `setlabel`, `gotolabel`, `getcallerpc`
  - `_idlehands`, `barriers`

## Important Behavior

- `_start` builds initial section mappings and L2 page tables before jumping into C `main`.
- Creates mappings for DRAM, IO registers, boot ROM, and kernel/user areas.
- Manages ARM control register bits for MMU, caches, branch prediction, alignment, and high vectors.
- Cache helpers use ARM CP15 operations and explicit wait/barrier loops.
- `tas` uses `LDREX`/`STREX` style exclusive access for atomic test-and-set.
- `spl*` manipulates IRQ/FIQ mask bits in CPSR.

## Dependencies And Assumptions

- Includes `arm.s`.
- Assumes the memory layout in `mem.h`, including `KZERO`, `L1`, and physical IO constants.
- Assumes single-core or simple exclusive access semantics matching this Kirkwood port.

## Notable Risks

- Startup page-table setup is tightly bound to physical address constants.
- Cache/MMU ordering errors here can corrupt all higher-level subsystems.
- Many routines are called from C via declarations in `fns.h`; signatures must stay synchronized.
