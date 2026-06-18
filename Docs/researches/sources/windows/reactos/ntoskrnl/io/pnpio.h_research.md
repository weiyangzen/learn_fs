# File Research: sources/windows/reactos/ntoskrnl/io/pnpio.h

## Role

`pnpio.h` is a small internal PnP I/O helper header. It declares debug/dump helpers for CM resource lists, IO resource requirement lists, individual descriptors, and device-node trees.

## Contents

- Dump flags define which device-node/resource views to print: all nodes, allocated resources, requirements, and translated resources (lines 4-8).
- Declared helpers include `PipDumpCmResourceList()`, `PipGetNextCmPartialDescriptor()`, `PipDumpCmResourceDescriptor()`, `PipDumpResourceRequirementsList()`, `PipDumpIoResourceDescriptor()`, and `PipDumpDeviceNodes()` (lines 10-52).

## Dependencies and use

The declarations use kernel PnP and resource types such as `PCM_RESOURCE_LIST`, `PCM_PARTIAL_RESOURCE_DESCRIPTOR`, `PIO_RESOURCE_REQUIREMENTS_LIST`, `PIO_RESOURCE_DESCRIPTOR`, and `PDEVICE_NODE`. Implementations are expected in PnP debug support code, not this header.

## Implementation gaps and risks

This file is declarations only. The only notable constraint is that callers depend on consistent flag meanings across the implementations.
