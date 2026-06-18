# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_rman.c

## Summary
Implements the kernel resource manager for bus/CPU hardware resource ranges, including allocation, sharing, activation, release, and sysctl enumeration.

## Main Responsibilities
- `rman_init()` / `rman_fini()` initialize and destroy resource managers.
- `rman_manage_region()` adds managed free regions.
- `rman_reserve_resource()` allocates ranges with alignment, sharing, and optional activation.
- `rman_activate_resource()` / `rman_deactivate_resource()` manage `RF_ACTIVE`.
- `rman_release_resource()` deallocates and merges adjacent free ranges.
- `rman_make_alignment_flags()` converts sizes to alignment flag encodings.
- `hw.bus.rman` sysctl exposes resource-manager and resource records.

## Important Behavior
Managed regions are kept in sorted TAILQs. Allocations split free regions into two or three pieces as needed. Shared allocations require exact compatible ranges and sharing flags. Timeshare activation rejects a resource if another sharer is already active.

## Risks
`RMAN_GAUGE` is explicitly unimplemented. `rman_manage_region()` is not robust against duplicate/overlapping region programming errors. Sysctl enumeration uses temporary holds to avoid teardown races; `rman_fini()` waits for these holds before freeing resources.
