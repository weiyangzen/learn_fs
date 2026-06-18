# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/arb/arbbus.c

## Role

`arbbus.c` defines the root bus-number arbiter instance wiring for the PnP manager. It is a skeleton for unpacking, packing, unpacking assigned resources, and scoring bus-number requirements.

## Main entry points and behavior

- `IopArbBusNumberUnpackRequirements()`, `IopArbBusNumberPackResource()`, `IopArbBusNumberUnpackResource()`, and `IopArbBusNumberScoreRequirement()` log their parameters, call `UNIMPLEMENTED`, and return `STATUS_NOT_IMPLEMENTED` or score `0` (lines 20-86).
- `IopArbBusNumberInitialize()` fills `IopRootBusNumberArbiter` with name `RootBusNumber` and the callback pointers above, then calls `ArbInitializeArbiterInstance()` for `CmResourceTypeBusNumber` on root path `Root` (lines 88-123).

## Dependencies

The file depends on the global `IopRootBusNumberArbiter` defined elsewhere and the arbiter library function `ArbInitializeArbiterInstance()`.

## Implementation gaps and risks

All resource translation/scoring callbacks are stubs, so the arbiter can be initialized but cannot correctly arbitrate bus-number requirements until those callbacks are implemented.
