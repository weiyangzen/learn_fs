# File Research: sources/windows/reactos/ntoskrnl/io/debug.c

## Purpose

`io/debug.c` provides diagnostic dump helpers for ReactOS I/O and PnP manager state. It prints CM resource lists, I/O resource requirements, device node state names, and recursive device-node trees.

## Resource Dumping

- `PipDumpCmResourceDescriptor()` prints one `CM_PARTIAL_RESOURCE_DESCRIPTOR` by resource type: port, interrupt, memory, DMA, device-specific, bus number, device-private, or unknown.
- `PipGetNextCmPartialDescriptor()` advances over fixed-size CM descriptors and accounts for variable-length device-specific data.
- `PipDumpCmResourceList()` walks each full resource descriptor in a `CM_RESOURCE_LIST` and dumps all partial descriptors.
- `PipDumpIoResourceDescriptor()` prints one `IO_RESOURCE_DESCRIPTOR` by type: null/generic, port, interrupt, memory, DMA, bus number, config data, device-private, or unknown.
- `PipDumpResourceRequirementsList()` walks all alternative resource lists in an `IO_RESOURCE_REQUIREMENTS_LIST`.

## Device-Node Dumping

- `PipGetDeviceNodeStateName()` maps `PNP_DEVNODE_STATE` values to readable strings and reports unknown states.
- `PipDumpArbiters()` is present but unimplemented.
- `PipDumpDeviceNode()` prints device-node level, devnode/PDO pointer, instance path, optional service name, problem code, and optional resource sections controlled by flags:
  - allocated and boot resources
  - required resources
  - translated resources
  - recursive child traversal
- `PipDumpDeviceNodes()` starts dumping from a caller-provided node or from `IopRootDeviceNode`.

## Important Details

- Most routines honor `DebugLevel`: level `0` always dumps, while nonzero levels compile out under `NDEBUG`.
- The code is diagnostic and uses `DPRINT1`; it does not modify I/O manager state.
- `PAGED_CODE()` appears in resource-list dump paths, constraining IRQL/pageability expectations.

## Research Notes

This file is not filesystem code, but it is relevant for storage and PnP investigation because it exposes resource allocation and device-tree inspection tools used around device discovery and boot storage debugging.
