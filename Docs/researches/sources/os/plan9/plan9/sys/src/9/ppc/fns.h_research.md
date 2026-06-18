# File Research: sources/os/plan9/plan9/sys/src/9/ppc/fns.h

## Role

PPC architecture function prototype header, extending `../port/portfns.h`.

## Contents

Declares CPU/register accessors, cache controls, delay and clock routines, trap/interrupt setup, MMU/TLB routines, floating-point save/restore, PCI config helpers, console/debug output, process save/restore, timers, alignment validation, and platform helpers. Defines `userureg`, `waserror`, `KADDR`, `PADDR`, `coherence`, `idlehands`, and no-op `kmapinval`.

## Dependencies

Used by nearly all PPC kernel C files. Many declarations correspond to assembly implementations or platform-specific code.

## Risks

Duplicate prototypes exist for several functions (`geticmp`, `puticmp`, `putsdr1`). Macro correctness for `KADDR`/`PADDR` underpins physical/virtual address handling across low-level drivers.
