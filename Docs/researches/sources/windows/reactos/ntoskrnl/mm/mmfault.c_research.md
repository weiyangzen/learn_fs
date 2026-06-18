# File Research: sources/windows/reactos/ntoskrnl/mm/mmfault.c

## Purpose

`mmfault.c` routes page faults between legacy ReactOS memory-area handlers and the newer ARM3 fault handler. It handles access faults, not-present faults, kernel/user permission checks, address-space locking, retry-on-memory-pressure behavior, and special cases such as shared user data and page-table addresses.

## Main Contents

- `MmpAccessFault` handles protection/access faults for legacy memory areas.
- `MmNotPresentFault` handles demand faults for legacy memory areas.
- `MmAccessFault` is the public dispatcher that decides whether a fault belongs to ARM3 or legacy ROSMM.
- Uses section-view handlers `MmAccessFaultSectionView` and `MmNotPresentFaultSectionView`.
- Under `NEWCC`, can dispatch cache-section faults to `MmAccessFaultCacheSection` or `MmNotPresentFaultCacheSection`.
- Calls `MmRebalanceMemoryConsumersAndWait` and retries when legacy handling returns `STATUS_NO_MEMORY`.

## Behavior And Data Flow

For legacy access and not-present faults, the code rejects high-IRQL faults, rejects user-mode access to kernel addresses, selects either the current process address space or kernel address space, locks the address space unless handling an MDL-style fault, locates the memory area, rejects missing/deleting areas, dispatches by memory-area type, and repeats if a handler requests `STATUS_MM_RESTART_OPERATION`.

The top-level `MmAccessFault` first gives i386 kernel PDE misses a chance to be repaired by `Mmi386MakeKernelPageTableGlobal`. It then immediately routes shared user data and page-table-address faults to ARM3. Once address spaces exist, it probes the relevant VAD tree; non-ROSMM VADs and paged-pool/no-address-space cases are routed to `MmArmAccessFault`. Remaining faults use the legacy access/not-present path.

## Concurrency And Invariants

- Fault handling below `DISPATCH_LEVEL` is required for both access and not-present legacy paths.
- Legacy memory-area lookup is protected by address-space locks except when `FromMdl` indicates the caller already controls locking.
- ARM3/legacy dispatch relies on VAD markers: ROSMM VADs are handled here, ARM3 VADs by `MmArmAccessFault`.
- Instruction-fetch faults on present pages are treated as NX violations and return `STATUS_ACCESS_VIOLATION`.

## Notable Details

- The `TrapInformation ? FALSE : TRUE` expression means absent trap information is treated as an MDL-originated fault for legacy handlers.
- Paged-pool faults can be routed to ARM3 even if no VAD was located.
- The file is a compatibility bridge: it preserves old ROSMM section/cache behavior while letting ARM3 own newer memory ranges.
