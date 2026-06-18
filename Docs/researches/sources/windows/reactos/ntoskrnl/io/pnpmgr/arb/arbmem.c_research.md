# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/arb/arbmem.c

## Role

`arbmem.c` defines root memory-resource arbiter callback wiring for the PnP manager. Its intended scope is memory-window requirement unpacking, resource descriptor packing/unpacking, and scoring.

## Main entry points and behavior

- `IopArbMemUnpackRequirements()`, `IopArbMemPackResource()`, `IopArbMemUnpackResource()`, and `IopArbMemScoreRequirement()` are debug-logged stubs returning `STATUS_NOT_IMPLEMENTED` or `0` (lines 20-86).
- `IopArbMemInitialize()` names the arbiter `RootMemory`, installs the memory callbacks, and initializes the arbiter instance (lines 88-113).

## Implementation gaps and risks

- Memory arbitration is not implemented beyond instance registration.
- The initializer passes `CmResourceTypeBusNumber` instead of a memory resource type, and the failure log names the DMA initializer, suggesting copy-paste errors (lines 101-109).
