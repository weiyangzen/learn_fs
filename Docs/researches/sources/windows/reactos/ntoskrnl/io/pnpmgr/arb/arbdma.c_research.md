# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/arb/arbdma.c

## Role

`arbdma.c` defines root DMA arbiter callback wiring for the PnP manager. Its intended job is DMA-channel resource requirement unpacking, resource packing/unpacking, and requirement scoring.

## Main entry points and behavior

- `IopArbDmaUnpackRequirements()`, `IopArbDmaPackResource()`, `IopArbDmaUnpackResource()`, and `IopArbDmaScoreRequirement()` are stubs that log inputs, call `UNIMPLEMENTED`, and return `STATUS_NOT_IMPLEMENTED` or score `0` (lines 20-86).
- `IopArbDmaInitialize()` names the arbiter `RootDma`, installs the DMA callbacks, and calls `ArbInitializeArbiterInstance()` (lines 88-113).

## Implementation gaps and risks

- The callback logic is unimplemented, so DMA resource arbitration cannot make meaningful decisions.
- The initializer passes `CmResourceTypeBusNumber` to `ArbInitializeArbiterInstance()` instead of a DMA resource type (lines 101-106). This looks copied from the bus-number initializer and is likely incorrect for a DMA arbiter.
