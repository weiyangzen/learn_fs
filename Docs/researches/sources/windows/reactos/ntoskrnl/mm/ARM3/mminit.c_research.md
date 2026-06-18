# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/mminit.c

## Role

`mminit.c` is the ARM3 memory-manager initialization implementation. It sizes and initializes physical-memory metadata, the PFN database, color tables, pool and system PTE regions, session-space layout, memory threshold events, system cache parameters, boot-loader memory release, and global tuning values used by later MM subsystems.

## Key mechanisms

- Defines the global memory layout state declared in `miarm.h`: nonpaged pool/system PTE boundaries, paged pool start/end/size, session-space boundaries, system view space, system cache, physical-memory descriptors, highest/lowest physical pages, user/kernel address split, PFN bitmap, memory threshold events, page coloring data, and system sizing/tuning variables.
- `MiScanMemoryDescriptors` walks the loader memory descriptor list, counts descriptors, excludes invisible memory from physical-page totals, finds lowest/highest physical PFNs, counts free pages, and selects the largest free descriptor for early contiguous boot allocations. `MxGetNextPage` then consumes pages from that descriptor and bugchecks if it runs dry.
- `MiComputeColorInformation` derives secondary page colors from L2 cache size/associativity, bounds the value to allowed min/max/default values, requires power-of-two colors, and publishes the mask to the current PRCB.
- `MiInitializeColorTables` maps and zeros the color-table storage immediately after the PFN database, then initializes zeroed/free page-color list heads for each color.
- Non-AMD64 PFN setup maps only regular physical memory into the PFN database. `MiMapPfnDatabase` maps PFN database pages using early free pages, `MiBuildPfnDatabaseFromPages` records already-valid startup PDE/PTE mappings, `MiBuildPfnDatabaseZeroPage` protects PFN 0 when appropriate, `MiBuildPfnDatabaseFromLoaderBlock` classifies free, bad, invisible, boot, and ROM loader pages, and `MiBuildPfnDatabaseSelf` accounts for pages backing the PFN database itself.
- `MmFreeLoaderBlock` gathers reclaimable loader ranges for registry, loader heap, and NLS data; under the PFN lock it either inserts unreferenced pages into the free list or clears/deletes referenced mappings and decrements share counts, then flushes the current TLB.
- `MiNotifyMemoryEvents`, `MiCreateMemoryEvent`, and `MiInitializeMemoryEvents` establish the public kernel memory condition events (`LowMemoryCondition`, `HighMemoryCondition`, paged-pool and nonpaged-pool variants), with ACLs that allow query rights to everyone and full access to administrators/system. Threshold defaults scale with physical memory.
- `MiAddHalIoMappings` scans HAL virtual address mappings and warns for valid HAL I/O mappings that lack PFN database entries, noting missing cache coherency/PAT tracking.
- `MmDumpArmPfnDatabase` is a diagnostic routine that raises IRQL, scans the PFN database, reports active/free/other pages, and when `MI_TRACE_PFNS` is enabled, buckets pages by usage class.
- `MmInitializeMemoryLimits` compacts included loader descriptors into a `PHYSICAL_MEMORY_DESCRIPTOR`, merging contiguous descriptors and resizing the allocation if the initial run estimate was too large.
- `MiBuildPagedPool` sizes paged pool, handles x86 VA constraints, initializes the shadow/double-mapped system page directory on two-level paging, allocates the first paged-pool PDE, initializes paged-pool allocation/end bitmaps, initializes paged pool and special pool, sets paged-pool thresholds, and initializes the global session-space map.
- `MmArmInitSystem` is the main phase-driven entry point. Phase 0 scans loader descriptors, initializes temporary event pointers, user/kernel address split, session layout, global lists/locks/events, system PTE sizing, heap and stack tuning, color information, PFN allocation sizing, machine-dependent setup, physical memory block and PFN bitmap, cached-range/HAL mapping checks, resident-page counts, large-page/driver lists, boot-driver relocation, system-size/product-type tuning, system cache bounds, commit limit, paged pool, debugger PTE, and loaded-module list.

## Dependencies and coupling

- Includes `miarm.h` and depends heavily on all ARM3 inline helpers, especially page-table address translation, PTE/PDE write helpers, PFN lock/list helpers, and system PTE reservation.
- Depends on loader-provided `LOADER_PARAMETER_BLOCK` and `MEMORY_ALLOCATION_DESCRIPTOR` ordering and type values.
- Calls machine- and subsystem-specific routines declared in `miarm.h`, including `MiInitMachineDependent`, `MiInitializeSessionSpaceLayout`, `MiInitializeLargePageSupport`, `MiInitializeDriverLargePageList`, `MiReloadBootLoadedDrivers`, `MiInitializeSystemPtes`, `MiInitializeSystemSpaceMap`, and pool initialization routines.
- Establishes globals consumed by later files in this group: `MmDebugPte` in `mmdbg.c`, working-set limits in `mmsup.c`, and cache/PTE templates used by `ncache.c`.

## Limitations and risks

- Several comments document incomplete or temporary behavior: registry configurability is not fully supported, system cache initialization is commented out, HAL I/O mapping cache coherency tracking is incomplete, driver verifier initialization is a FIXME, and many values are hardcoded NT-like defaults.
- Physical-memory initialization is architecture-conditional. The non-AMD64 path contains substantial PFN database construction that is not compiled on AMD64.
- Early allocation relies on the largest free loader descriptor and bugchecks if it cannot satisfy required PFN/color-table mappings.
- `MmArmInitSystem` returns success unconditionally outside explicit failure paths and contains a large amount of policy in one initializer, making order dependencies important.
