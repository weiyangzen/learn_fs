# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/iorsrce.c

## Purpose

Implements hardware resource and configuration-query support for the ReactOS I/O manager, including legacy hardware registry traversal, configuration information reporting, system partition persistence, legacy resource assignment, and HAL resource map registration.

## Main Responsibilities

- Maintains global `CONFIGURATION_INFORMATION` returned by `IoGetConfigurationInformation`.
- Maps ARC `CONFIGURATION_TYPE` and `IO_QUERY_DEVICE_DATA_FORMAT` values to registry value/key names.
- Traverses `\REGISTRY\MACHINE\HARDWARE\DESCRIPTION\SYSTEM` to implement `IoQueryDeviceDescription`.
- Fetches enabled device interfaces for configuration checks.
- Stores system partition and OS loader path data in `HKLM\SYSTEM\Setup`.
- Handles legacy resource reporting and assignment with conflict detection.
- Writes HAL raw and translated resources into `\Registry\Machine\HARDWARE\RESOURCEMAP`.

## Key Functions

- `IopQueryDeviceDescription` walks controller and peripheral registry keys, collects identifier/configuration/component values, and invokes the caller’s query callback.
- `IopQueryBusDescription` recursively enumerates root and sub-bus keys, matches requested interface type and bus number, then either calls the query callback directly or descends into controller/peripheral lookup.
- `IopFetchConfigurationInformation` calls `IoGetDeviceInterfaces`, counts returned symbolic links, and compares against an expected interface count.
- `IopStoreSystemPartitionInformation` resolves the system partition symbolic link target and writes `SystemPartition` and normalized `OsLoaderPath` registry values.
- `IoGetConfigurationInformation` returns the static global configuration structure.
- `IoReportResourceUsage` is half-implemented: validates resource input, detects conflicts, respects `OverrideConflict`, but does not claim resources in the registry.
- `IopLegacyResourceAllocation` is half-implemented: fixes resource lists against requirements, detects conflicts, but does not persist claims; null requirements return `STATUS_NOT_IMPLEMENTED`.
- `IoAssignResources` rejects inappropriate use by non-legacy PnP device nodes and delegates to legacy allocation.
- `IoQueryDeviceDescription` initializes root registry traversal and query context.
- `IoReportHalResourceUsage` creates volatile resource-map keys and writes `.Raw` and `.Translated` resource-list values.

## Filesystem Relevance

This file is not filesystem-specific, but it is part of the same I/O manager substrate that storage, disk, bus, and filesystem stacks rely on during boot and legacy driver initialization. Resource assignment and hardware description queries affect device discovery paths below filesystems.

## Dependencies and Coupling

Depends on registry syscalls, Unicode string construction, pool allocation, PnP device nodes, resource conflict detection/fixup helpers, device interface enumeration, object symbolic links, and HAL resource descriptors.

## Research Notes

- Resource reporting/assignment is explicitly incomplete where registry claiming should happen.
- `IoQueryDeviceDescription` only proceeds when `BusType` is supplied; missing bus type returns `STATUS_NOT_IMPLEMENTED`.
- The recursive registry traversal allocates and frees many `KEY_*_INFORMATION` buffers; cleanup paths are central to correctness.
