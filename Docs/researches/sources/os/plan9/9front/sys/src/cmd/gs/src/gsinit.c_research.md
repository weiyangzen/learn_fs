# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsinit.c

## Role

`gsinit.c` initializes and finalizes the Ghostscript imager/library runtime.

This is library lifecycle infrastructure, not filesystem code.

## Main Interfaces

- `gs_lib_init`
- `gs_lib_init0`
- `gs_lib_init1`
- `gs_lib_finit`

## Core Behavior

- `gs_lib_init0` creates the default malloc-backed Ghostscript memory allocator, clears debug flags, and disables error logging.
- `gs_lib_init1` iterates the generated `gx_init_table` and runs each configuration-specific initialization procedure.
- `gs_lib_init` composes those two stages.
- `gs_lib_finit` calls platform cleanup via `gp_exit`.

## Notable Risks

The finalizer comments note an interface problem: it cannot always know whether it owns the allocator and therefore does not release `mem` here.
