# File Research: sources/os/linux/linux/mm/Makefile

## Purpose
Defines object composition, instrumentation exclusions, and configuration-gated build rules for the Linux memory-management subsystem.

## Main Contents
- Disables KASAN/KCSAN/KCOV instrumentation for selected allocator, page allocator, kmemleak, memcg, vmstat, and related objects where instrumentation is noisy or unsafe.
- Builds the core MM object set: filemap, writeback, reclaim, swap core, shmem, slab, page allocation, memblock, backing-dev, percpu, compaction, GUP, VMAs, and MMU/NOMMU-specific files.
- Selects optional objects for swap/zswap, DMA pools, hugetlb, NUMA, sparsemem, MMU notifier, KSM, sanitizers, migration, memcg, CMA, ballooning, page extension, secretmem, userfaultfd, DAMON, hardened usercopy, zone device, HMM, page reporting, bootmem info, and tests.

## Integration Points
Directly consumes symbols from `mm/Kconfig` and architecture Kconfig. It also assigns module-parameter namespaces through aggregate targets such as `page-alloc-y` and `memory-hotplug-y`.

## Notable Behaviors
- `mmu-y` is `nommu.o` by default and replaced with the normal MMU object list when `CONFIG_MMU=y`.
- `bpf_memcontrol.o` is only built when both memcg and BPF syscall support are enabled.
- CMA support is split into core, debugfs, and sysfs objects by config.
- KCSAN barrier instrumentation is explicitly enabled while KCSAN is disabled for noisy allocator files.

## Risks And Review Focus
- Build-rule ordering and config guards determine which subsystem code is linked into every kernel.
- Instrumentation exclusions should be reviewed before adding sanitizer-sensitive MM code.
- Optional object additions must match Kconfig dependencies to avoid unresolved symbols.
