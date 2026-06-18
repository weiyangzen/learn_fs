# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/hppa/pthread_md.h

## Purpose
HPPA machine-dependent pthread helpers.

## Main Responsibilities
- Enables `PTHREAD__ASM_RASOPS`.
- Defines `pthread__sp()` from register `r30`.
- Defines ucontext stack pointer access via `_REG_SP`.
- Initializes PSW to `0x4000f`.
- Defines `STACKSPACE` as `HPPA_FRAME_SIZE`.
- Marks pthread atomics as already memory-barrier-safe.

## Dependencies
- `machine/frame.h` and HPPA mcontext layout.
