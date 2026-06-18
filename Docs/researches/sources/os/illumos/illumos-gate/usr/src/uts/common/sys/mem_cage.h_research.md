# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mem_cage.h

Purpose: Declares kernel memory-caging interfaces and state.

Key definitions:
- Cage creation return/status constants: `KCT_FAILURE`, `KCT_CRIT`, `KCT_NONCRIT`.
- Global cage state and thresholds: enable flags, cageout thread, free/need/lots/des/min/throttle free counts.
- Direction enum: `KCAGE_UP`, `KCAGE_DOWN`.

Key APIs:
- Free-memory accounting: `kcage_freemem_add/sub()`.
- Throttle and range setup: `kcage_create_throttle()`, `kcage_range_init()`, `kcage_range_add()`.
- Range queries/deletion: `kcage_current_pfn()`, `kcage_range_delete()`, `kcage_range_delete_post_mem_del()`.
- Threshold recalculation and pageout/clock hooks: `kcage_recalc_thresholds()`, `kcage_cageout_init()`, `kcage_cageout_wakeup()`, `kcage_tick()`.
- Pagelist integration: `kcage_next_range()`.

Relevance to subset A: Kernel physical memory management, relevant to memory delete/relocation behavior.
