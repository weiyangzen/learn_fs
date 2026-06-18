# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/pnp.c

## Purpose

`pnp.c` contains the VFAT PnP major-function handler.

## Behavior

- `VfatPnp()` asserts a valid IRP context.
- It returns `STATUS_NOT_IMPLEMENTED` for:
  - `IRP_MN_QUERY_REMOVE_DEVICE`
  - `IRP_MN_SURPRISE_REMOVAL`
  - `IRP_MN_REMOVE_DEVICE`
  - `IRP_MN_CANCEL_REMOVE_DEVICE`
- For all other PnP minor functions, it skips the current IRP stack location, clears `IRPCONTEXT_COMPLETE`, and forwards the IRP to the lower storage device.

## Research Notes

Removal handling is effectively incomplete. For non-removal PnP requests, VFAT behaves as a pass-through layer and relies on the lower device stack for completion.
