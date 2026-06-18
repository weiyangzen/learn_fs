# File Research: sources/os/plan9/9front/sys/src/9/teg2/mmu.c

ARMv7 MMU setup and per-process mapping for Tegra 2.

Purpose:
- Builds kernel mappings, device mappings, high-vector mappings, and per-process user page tables.
- Provides runtime mapping helpers used by VM and device code.

Key behavior:
- `mmuinit` maps IO/NOR/AHB regions, creates high-vector L2 mapping, makes kernel text read-only, and clears user L1 space.
- `expand` converts 1 MiB ARM section mappings into coarse L2 tables when fine-grained page mappings are needed.
- `mmuswitch`, `flushmmu`, `mmurelease`, and `putmmu` maintain process user mappings via `Proc.mmul2`.
- `mmuuncache`, `mmukmap`, `mmukunmap`, `vmap`, and `vunmap` provide limited kernel/device mapping helpers.
- Uses explicit L1/L2 cache writeback and TLB invalidation around page-table changes.

Integration:
- Depends on `l.s` CP15/TLB/cache primitives and `main.c` `l2pages` reservation.
- Feeds Plan 9 VM fault handling through `putmmu`.

Risks/notes:
- Comments state L2 cache ops are empirically required for page tables.
- L2 page allocation wastes full pages for 1 KiB ARM coarse tables.
- `mmul1empty` contains disabled incremental-clearing code marked buggy.
