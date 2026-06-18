# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnpdma.c

This small file implements `IoGetDmaAdapter`, the PnP-aware DMA adapter lookup routine.

Behavior:
- If a `PhysicalDeviceObject` is supplied and the caller's `DEVICE_DESCRIPTION.InterfaceType` is `PNPBus` or `InterfaceTypeUndefined`, the function copies the description and tries to fill a concrete legacy bus type from `IoGetDeviceProperty(DevicePropertyLegacyBusType)`.
- It sends `IRP_MN_QUERY_INTERFACE` for `GUID_BUS_INTERFACE_STANDARD` through `IopInitiatePnpIrp`.
- On success, it calls the bus interface's `GetDmaAdapter` with the effective device description and caller's `NumberOfMapRegisters`, then releases the bus interface with `InterfaceDereference`.
- If the bus does not return an adapter, or if there is no PDO, it falls back to `HalGetDmaAdapter`.

Integration points:
- Depends on WDM bus-interface support from the device stack.
- Falls back to HAL behavior, so callers can use one API for bus-provided and platform-provided DMA adapter allocation.

Research notes:
- The queried `BUS_INTERFACE_STANDARD` structure is stack allocated and used only within the successful query path.
- Interface type fallback sets the copied description to `Internal` when the legacy bus type property query fails.
