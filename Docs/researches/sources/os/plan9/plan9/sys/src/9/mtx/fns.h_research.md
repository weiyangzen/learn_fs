# File Research: sources/os/plan9/plan9/sys/src/9/mtx/fns.h

## Role

Machine-dependent function declaration header for the MTX PowerPC port. It declares assembly helpers, interrupt/timer/MMU routines, PCI and I/O port access, Ethernet/keyboard setup, and process transition hooks.

This is platform infrastructure used by drivers and kernel subsystems.

## Main Interfaces

- Includes `../port/portfns.h`.
- PowerPC helpers:
  - `getmsr`, `putmsr`, `getpvr`, `getdec`, `putdec`
  - `getdar`, `getdsisr`, `gethid0`, `puthid0`, `sync`, `eieio`
- I/O port helpers:
  - `inb`, `insb`, `ins`, `inss`, `inl`, `insl`
  - `outb`, `outsb`, `outs`, `outss`, `outl`, `outsl`
- Interrupt and timer:
  - `i8259init`, `i8259enable`, `i8259disable`, `intrenable`
  - `clockinit`, `clockintr`, `timeradd`, `timerdel`
- MMU/cache:
  - `mmuinit`, `mmusweep`, `tlbflush`, `tlbflushall`, `icflush`, `dcflush`
- PCI:
  - `pciscan`, `pcimatch`, `pcicfgr*`, `pcicfgw*`
- Process/control:
  - `touser`, `trapvec`, `forkret`, `procsetup`, `procsave`

## Important Macros

- `coherence()` maps to `eieio()`.
- `cycles(x)` is a no-op.
- `idlehands()` and `kexit(a)` are no-ops.
- `userureg(ur)` tests `MSR_PR`.
- `KADDR`/`PADDR` map through `KZERO`.

## Dependencies And Assumptions

- Assumes PowerPC assembly symbols from `mtx/l.s` and `inb.s`.
- Assumes MTX memory layout macros from `mem.h`.

## Notable Risks

- Several port hooks are stubbed/no-op for this architecture.
- Simple address conversion macros assume direct kernel mapping.
