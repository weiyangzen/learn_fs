# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/arb/arbirq.c

## Role

`arbirq.c` defines root IRQ arbiter callback wiring for the PnP manager. It is intended to arbitrate interrupt-line resources.

## Main entry points and behavior

- `IopArbIrqUnpackRequirements()`, `IopArbIrqPackResource()`, `IopArbIrqUnpackResource()`, and `IopArbIrqScoreRequirement()` are unimplemented stubs with debug logging (lines 20-86).
- `IopArbIrqInitialize()` names the arbiter `RootIRQ`, installs the IRQ callbacks, and initializes the arbiter instance (lines 88-113).

## Implementation gaps and risks

- The actual IRQ translation and scoring logic is absent.
- The initializer passes `CmResourceTypeBusNumber` rather than an interrupt resource type, and the failure log message says `IopArbDmaInitialize`, both indicating copy-paste defects (lines 101-109).
