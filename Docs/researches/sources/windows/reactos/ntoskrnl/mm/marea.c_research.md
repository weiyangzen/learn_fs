# File Research: sources/windows/reactos/ntoskrnl/mm/marea.c

## Purpose

`marea.c` implements legacy ReactOS memory areas backed by VAD-like AVL nodes. It creates, locates, inserts, frees, and cleans up `MEMORY_AREA` objects for section views, cache views, and static ARM3-owned kernel ranges while coexisting with newer ARM3 VADs.

## Main Contents

- Defines static memory-area storage and the legacy kernel VAD root `MiRosKernelVadRoot`.
- Locates areas by address or range with `MmLocateMemoryAreaByAddress` and `MmLocateMemoryAreaByRegion`.
- Checks address availability with `MmIsAddressRangeFree`.
- Inserts memory areas into process VAD roots or the legacy kernel VAD root through `MmInsertMemoryArea`.
- Finds free address gaps with `MmFindGap`.
- Frees mappings and VAD nodes through `MmFreeMemoryArea`.
- Creates memory areas through `MmCreateMemoryArea`.
- Cleans up process-exit legacy areas with `MiRosCleanupMemoryArea`.

## Behavior And Data Flow

`MmCreateMemoryArea` allocates either from a static array or nonpaged pool, initializes the object as a memory-area VAD, optionally finds a gap, validates user/kernel boundaries, checks conflicts for non-ARM3-owned areas, and inserts the VAD into the appropriate AVL table. User memory areas are inserted into the owning process VAD root; kernel areas are inserted into `MiRosKernelVadRoot`, initialized lazily.

`MmFreeMemoryArea` walks every page in the area. It removes swap mappings, physical mappings, or virtual mappings depending on page state and callback usage, invokes an optional page-free callback, removes the VAD node from the appropriate tree, detaches if it had attached to another process, poisons the magic in debug builds, and frees the area.

## Concurrency And Invariants

- Callers must hold the address-space creation lock; `MmFreeMemoryArea` asserts ownership.
- Process VAD operations use process working-set locks; kernel legacy VAD operations use `MmSystemCacheWs`.
- User memory areas must not cross `MmSystemRangeStart`; kernel address spaces must not allocate below it.
- ARM3-owned memory areas bypass some legacy conflict checks because their ranges are assumed prevalidated.

## Notable Details

- `MmLocateMemoryAreaByRegion` filters out ARM3 VADs by checking `MI_IS_MEMORY_AREA_VAD`; it returns only legacy memory areas.
- `MiRosCleanupMemoryArea` is explicitly constrained to process teardown and supports section views plus optional NEWCC cache areas.
- Static ARM3 memory areas are used during initialization to reserve important kernel ranges while still representing them in the legacy memory-area tree.
