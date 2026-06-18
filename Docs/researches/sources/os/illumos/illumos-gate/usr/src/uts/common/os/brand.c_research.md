# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/brand.c

## Purpose

`brand.c` implements common illumos branded-zone process support. It manages registered kernel brands, zone references to brands, process brand transitions, SPARC syscall interposition hooks, and helper logic for Solaris-derived brands during `exec`, fork, LWP lifecycle, and process exit.

## Main Interfaces

Brand registry and zone lifecycle: `brand_init`, `brand_register`, `brand_unregister`, `brand_register_zone`, `brand_zone_count`, `brand_unregister_zone`.

Process lifecycle: `brand_setbrand`, `brand_clearbrand`, `brand_solaris_copy_procdata`, `brand_solaris_exec`, `brand_solaris_fini`, `brand_solaris_forklwp`, `brand_solaris_freelwp`, `brand_solaris_initlwp`, `brand_solaris_lwpexit`, `brand_solaris_proc_exit`, `brand_solaris_setbrand`.

Brand syscall/exec helpers: `brand_solaris_cmd`, `brand_solaris_elfexec`.

SPARC-only helpers: `brand_plat_interposition_enable`, `brand_plat_interposition_disable`.

## Behavior

The global `brand_list` tracks loaded brands and per-brand zone reference counts under `brand_list_lock`. Registration rejects malformed brands, unsupported versions, and duplicate names. Zone registration may dynamically load `brand/<module>` with `ddi_modopen()` and then increments the matching brand refcount.

`brand_setbrand()` is called from exec for a single-threaded process, changes `p_brand`, and calls the brand’s `b_setbrand` operation. `brand_clearbrand()` calls `b_proc_exit` and restores the native brand.

On SPARC, the first non-native brand enables global syscall interposition by hot-patching trap-table patch points to branch to syscall wrappers. The last unregister restores original instructions.

`brand_solaris_cmd()` handles common branded syscall commands: executing native binaries, registering the user-space syscall handler, returning saved ELF data, and providing a truss visibility point.

`brand_solaris_elfexec()` is the largest path. It first execs the brand emulation library, saves its aux-vector data, maps the target executable and optional branded linker, rewrites process exec environment and aux vectors so debuggers see target program data, emits brand-specific aux vectors for the emulation library, sets `AF_SUN_NOPLM`, and clears `spd_handler` until user-space brand initialization completes.

## Notable Invariants

- Brand operations generally assume single-threaded exec context.
- `p_brand_data` exists for branded processes and is freed on process exit.
- Registered brand modules cannot unload while zones reference them.
- Labeled systems reject branded zones.
- SPARC interposition changes are protected by `brand_list_lock` and only enabled while brands are loaded.

## Dependencies

This file depends on zone state, process/LWP structures, brand machine operations, module loading, ELF exec helpers, aux-vector layout, vnode lookup/release, copyin/copyout, and platform hot-patching.

## Research Notes

Audit hotspots are `brand_solaris_elfexec()` error unwinding after partial exec-environment changes, aux-vector rewriting for 32-bit versus native models, dynamic module/brand-name mismatch handling, and SPARC syscall patch restoration.
