# File Research: sources/os/plan9/plan9/sys/src/9/kw/fns.h

## Role

Machine-dependent function declaration header for the Kirkwood ARM Plan 9 port. It binds architecture assembly, MMU/cache operations, interrupt functions, PCI helpers, FPU hooks, UART console routines, and port-layer compatibility macros.

This is platform infrastructure used by storage and filesystem-adjacent drivers, but contains no filesystem logic itself.

## Main Interfaces

- Includes `../port/portfns.h`.
- Cache/MMU/CPU helpers:
  - `cachedwb`, `cachedwbinv`, `cachedinv`, `cacheiinv`
  - `l1cacheson`, `l1cachesoff`, `l2cache*`
  - `mmuidmap`, `mmuinvalidate`, `mmukmap`, `mmukunmap`, `vmap`, `vunmap`
- Coprocessor/register helpers:
  - `cpctget`, `cpidget`, `controlget`, `cprd`, `cpwr`, `fsrget`, `farget`
- Trap/interrupt entry points:
  - `vectors`, `vtable`, `intrenable`, `intrdisable`
- FPU emulation hooks:
  - `fpiarm`, `fpuemu`, `fpuprocsave`, `fpuprocrestore`
- PCI configuration helpers.
- Memory allocation aliases for SD and uncached allocation.

## Important Macros

- `coherence` maps to `barriers`.
- `cycles(ip)` stores `lcycles()` into the supplied pointer.
- `CASU`, `CASV`, `CASW` use `cas32`.
- `KADDR` and `PADDR` perform simple segment masking for kernel/physical conversion.
- `waserror()` expands to Plan 9 error-label stack setup.

## Dependencies And Assumptions

- Assumes ARM Kirkwood assembly symbols from `l.s`, `lexception.s`, and `lproc.s`.
- Assumes Plan 9 `Proc`, `Ureg`, `Pcidev`, `Block`, and allocation APIs exist.
- `KADDR`/`PADDR` are simple segment conversions, so callers must not pass arbitrary unmapped addresses.

## Notable Risks

- Header mixes public prototypes, macros, and low-level compatibility shims.
- Several macros hide architecture-specific behavior and are unsafe if reused outside this address-space model.
