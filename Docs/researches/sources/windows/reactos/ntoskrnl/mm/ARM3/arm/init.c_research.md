# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/arm/init.c

Read status: complete file, 72 lines.

This ARM-specific ARM3 memory-manager initialization file mostly declares global memory layout and accounting variables expected by the broader ARM3 memory manager, with machine-dependent initialization still stubbed.

Key contents:
- Global nonpaged/paged/session/system view layout variables such as `MmNonPagedSystemStart`, `MmNonPagedPoolStart`, `MmPagedPoolEnd`, `MmSessionBase`, and `MiSystemViewStart`.
- PFN and physical-memory globals including `MmSystemPageDirectory`, `MmSystemPagePtes`, `MiPfnBitMap`, `MmPhysicalMemoryBlock`, `MmNumberOfPhysicalPages`, and `MmHighestPhysicalPage`.
- User/kernel range globals such as `MmUserProbeAddress`, `MmHighestUserAddress`, `MmSystemRangeStart`, `MmSystemCacheStart`, and `MmHyperSpaceEnd`.
- `MiInitMachineDependent()` is the only function and calls `UNIMPLEMENTED_FATAL()` before returning success.

Important dependencies:
- Shared ARM3 internals from `mm/ARM3/miarm.h`.
- Loader-provided memory descriptors through `PLOADER_PARAMETER_BLOCK`, though not yet consumed here.

Notable behavior:
- This file is a declaration/porting placeholder for ARM memory-manager state.
- `MiInitMachineDependent()` is not functionally implemented; it fatal-logs unimplemented initialization.
