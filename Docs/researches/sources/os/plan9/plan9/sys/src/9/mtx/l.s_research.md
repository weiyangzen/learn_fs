# File Research: sources/os/plan9/plan9/sys/src/9/mtx/l.s

## Role

Core PowerPC assembly for the MTX port. It provides early MMU/BAT setup, interrupt priority primitives, context switch labels, cache/TLB operations, atomic primitives, special-register access, trap vector entry, user-mode transition, and FPU save/restore.

This is low-level kernel architecture support, not filesystem code.

## Main Interfaces

- Globals:
  - `mach0`
  - `memsize`
- MMU/bootstrap:
  - `mmuinit0`
  - `tlbflushall`
  - `tlbflush`
- FPU:
  - `kfpinit`
  - `fpsave`
  - `fprestore`
- Interrupt priority:
  - `splhi`
  - `splx`
  - `splxpc`
  - `spllo`
  - `spldone`
  - `islo`
- Context/process:
  - `setlabel`
  - `gotolabel`
  - `touser`
  - `forkret`
- Cache/atomic:
  - `icflush`
  - `dcflush`
  - `tas`
  - `_xinc`
  - `_xdec`
  - `cmpswap`
- Register access:
  - `getpvr`, `getdec`, `putdec`, `getdar`, `getdsisr`
  - `getmsr`, `putmsr`, `putsdr1`, `putsr`
  - `gethid0`, `gethid1`, `puthid0`, `puthid1`
  - `eieio`, `sync`
- Trap entry:
  - `trapvec`
  - `saveureg`
  - internal `ktrap` and `restoreureg`

## Important Behavior

- Initializes block address translation and segment registers for kernel mappings.
- Implements spin/atomic primitives with PowerPC reservation instructions.
- Saves complete trap frames into `Ureg` layout before calling C `trap`.
- Restores user state and returns with `RFI`.
- FPU save/restore covers 32 floating registers and FPSCR.
- Provides cache flush loops over address ranges.

## Dependencies And Assumptions

- Includes `mem.h`.
- Assembly uses fixed offsets in `Mach`, `Proc`, and `Ureg`; these must match C headers.
- Assumes PowerPC exception and MSR semantics.

## Notable Risks

- Struct offset drift breaks traps, scheduling, and user transitions.
- BAT/MMU setup is board-specific and fragile.
- FPU save/restore layout must match `FPsave` exactly.
