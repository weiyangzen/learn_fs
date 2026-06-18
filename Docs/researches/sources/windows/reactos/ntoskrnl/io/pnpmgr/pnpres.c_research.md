# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnpres.c

Read status: complete file, 1498 lines.

This file implements PnP resource allocation, requirement filtering, resource-list translation, resource-map persistence, and conflict detection against the registry-backed hardware resource map.

Key entry points:
- `IopFindBusNumberResource()`, `IopFindMemoryResource()`, `IopFindPortResource()`, `IopFindDmaResource()`, and `IopFindInterruptResource()` search for available descriptors satisfying individual `IO_RESOURCE_DESCRIPTOR` requirements.
- `IopFixupResourceListWithRequirements()` merges existing boot/assigned resources with one acceptable alternative list from an `IO_RESOURCE_REQUIREMENTS_LIST`, adding missing descriptors and handling alternates.
- `IopFilterResourceRequirements()` sends `IRP_MN_FILTER_RESOURCE_REQUIREMENTS` to the device stack and adopts a returned requirements list if one is supplied.
- `IopTranslateDeviceResources()` copies raw resources and translates ports, interrupts, and memory through HAL routines.
- `IopAssignDeviceResources()` is the high-level assignment flow: filter requirements, copy boot resources, detect conflicts, call `HalAdjustResourceList()`, fix up missing resources, translate, update `HARDWARE\\RESOURCEMAP`, update Enum `Control\\AllocConfig`, and set `DeviceNodeResourcesAssigned`.
- `IopDetectResourceConflict()` walks `\\Registry\\Machine\\HARDWARE\\RESOURCEMAP`, skips `.Translated` values, and compares raw resource lists.
- `IopUpdateResourceMap()` and `IopUpdateControlKeyWithResources()` persist raw/translated resources in global and per-device registry locations.

Important dependencies:
- Resource-list sizing from `PnpDetermineResourceListSize()`.
- Registry resource map layout under `HARDWARE\\RESOURCEMAP`.
- HAL translation/adjustment: `HalTranslateBusAddress`, `HalGetInterruptVector`, `HalAdjustResourceList`.
- Device properties for PDO names through `IoGetDeviceProperty(DevicePropertyPhysicalDeviceObjectName)`.
- PnP IRP helper `IopInitiatePnpIrp()`.

Notable behavior and risks:
- `IopCheckResourceDescriptor()` detects overlap for memory, port, interrupt, bus-number, and DMA descriptors, but returns `FALSE` for non-silent checks due to a local hack; this suppresses real conflict failures in some user-visible paths.
- When a conflict is found and a conflicting descriptor is requested, the code copies the incoming descriptor rather than the already-owned conflicting descriptor, weakening range-skip logic in resource search.
- Memory and port allocation mutate zero alignment to one as a workaround.
- Resource-list walking comments acknowledge variable-sized `CmResourceTypeDeviceSpecific` descriptors, but several loops still index `PartialDescriptors[ii]` directly.
- `IopTranslateDeviceResources()` has a missing `break` after memory translation, intentionally or accidentally falling through to no-op descriptor cases.
- On translation cleanup, the translated-list free path assigns `DeviceNode->ResourceList = NULL` twice and does not clear `ResourceListTranslated`.
