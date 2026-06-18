# File Research: sources/os/linux/linux/mm/Kconfig

## Purpose
Defines the kernel memory-management configuration menu and feature dependencies for swap, allocators, memory models, migration, compaction, huge pages, CMA, memory hotplug, device memory, userfaultfd, MGLRU, and architecture MM feature hooks.

## Main Contents
- Swap and compression: `SWAP`, `ZSWAP`, default zswap compressor choices, zswap shrinker defaults, and `ZSMALLOC` options.
- Slab/page hardening and observability: SLUB, freelist randomization/hardening, kmalloc bucket separation, SLUB stats, random kmalloc caches, page allocator shuffle, and heap-randomization compatibility.
- Memory model/hotplug: FLATMEM/SPARSEMEM/VMEMMAP selection, memory-hotplug online defaults, hot-remove, memmap-on-memory, and bootmem info hooks.
- Reclaim/migration/compaction: balloon migration, compaction, page reporting, NUMA migration, generic migration, contig allocation, and PCP batch scaling.
- User-visible MM features: KSM, memory failure recovery, THP policy defaults, read-only file THP, soft-dirty tracking, secretmem, anonymous VMA names, GUP tests, userfaultfd, MGLRU, per-VMA locks, NUMA emulation, and lazy MMU mode tests.
- CMA and device memory: CMA core/debugfs/sysfs, maximum CMA areas, pageblock order bounds, ZONE_DMA/DMA32/DEVICE, HMM mirror, DEVICE_PRIVATE, and PFNMAP support.

## Integration Points
Feeds conditional compilation across `mm/Makefile`, architecture Kconfig selections, documentation-described sysfs/proc/kernel-command-line controls, and dependent subsystems such as zram/zswap, hugetlb, DAX/HMM, memcg, DAMON, and userfaultfd.

## Notable Behaviors
- Many symbols are architecture-selected capability hooks rather than direct user choices.
- Several defaults are intentionally conservative, especially for debug/statistics, THP submodes, hotplug online policy, and experimental mapcount/THP options.
- CMA depends on MMU and selects migration plus memory isolation.
- The file sources `mm/damon/Kconfig` before ending the Memory Management menu.

## Risks And Review Focus
- Dependency changes can silently alter build coverage across architectures.
- Defaults affect boot-time policy and runtime ABI expectations under `/sys`, `/proc`, and command-line parameters.
- Experimental options such as read-only THP for filesystems and no per-page mapcount need careful compatibility review.
