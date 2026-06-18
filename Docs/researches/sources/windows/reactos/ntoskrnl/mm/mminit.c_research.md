# File Research: sources/windows/reactos/ntoskrnl/mm/mminit.c

## Purpose

`mminit.c` performs phase-1 memory-manager initialization for the ReactOS kernel. It creates static memory areas for important kernel virtual ranges, initializes legacy and ARM3 memory-manager subsystems, sets up shared user data mapping support, starts memory-management system threads, initializes memory events/session support, and write-protects loaded system images.

## Main Contents

- Defines globals such as `Mm64BitPhysicalAddress`, `MmReadClusterSize`, `MmDisablePagingExecutive`, `MmSharedUserDataPte`, and `MmKernelAddressSpace`.
- `MiCreateArm3StaticMemoryArea` creates a static `MEMORY_AREA_OWNED_BY_ARM3` reservation.
- `MiInitSystemMemoryAreas` reserves loader image, PTE base, hyperspace, PFN database, nonpaged pool, system PTEs, nonpaged expansion, system views, session space, paged pool, debugger mapping, and architecture-specific HAL/KPCR/shared-data ranges.
- `MiDbgDumpAddressSpace` prints the initialized kernel memory layout.
- `MmInitBsmThread` starts the balance set manager thread.
- `MmInitSystem` wires together all phase-1 initialization steps.

## Behavior And Data Flow

`MmInitSystem` asserts phase 1, initializes cache/section synchronization primitives, sets the kernel address space to the idle process VM, builds static kernel memory areas, dumps the layout, initializes global kernel page directories, memory consumers, reverse maps, section implementation, and pagefile support. It allocates a paged-pool PTE template for `KI_USER_SHARED_DATA`, initializes session working-set and session ID support, initializes memory threshold events, starts balancer and balance-set-manager threads, and finally walks loaded modules to apply system image write protection.

## Concurrency And Invariants

- Static memory-area creation runs under the kernel address-space lock.
- Each static area is asserted to create successfully; the helper notes that a bugcheck might be more appropriate than assertion-only handling.
- `MmSharedUserDataPte` is allocated from paged pool because the fault handler can already handle paged-pool addresses before it is used.
- Loaded module write-protection runs under `PsLoadedModuleResource`.

## Notable Details

- The loader image is the only static memory area marked executable by this file; other reserved ranges are read/write.
- The file initializes both old ROSMM pieces and newer ARM3 infrastructure, mirroring the hybrid design visible in `marea.c` and `mmfault.c`.
- `MmDisablePagingExecutive` is hard-coded to `1`, with comments noting paging executive states.
