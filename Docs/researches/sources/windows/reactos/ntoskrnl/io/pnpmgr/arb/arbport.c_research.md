# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/arb/arbport.c

## Role

`arbport.c` defines root I/O port arbiter callback wiring for the PnP manager. It is intended to handle port-range resource requirement unpacking, assignment packing/unpacking, and scoring.

## Main entry points and behavior

- `IopPortMemUnpackRequirements()`, `IopPortMemPackResource()`, `IopPortMemUnpackResource()`, and `IopPortMemScoreRequirement()` are unimplemented stubs with debug logging (lines 20-86).
- `IopArbPortInitialize()` names the arbiter `RootPort`, installs those callbacks, and calls `ArbInitializeArbiterInstance()` (lines 88-113).

## Implementation gaps and risks

- I/O port arbitration behavior is absent.
- Callback names include `PortMem`, which may be a naming error for port resources.
- The initializer passes `CmResourceTypeBusNumber` instead of a port resource type, and the failure log names the DMA initializer, both likely copy-paste defects (lines 95-109).
