# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/adapter.c

## Purpose

`adapter.c` contains I/O manager wrapper state for HAL adapter APIs and implements `IoAllocateAdapterChannel()`.

## Contents

- Defines global object-type pointers:
  - `IoAdapterObjectType`
  - `IoDeviceHandlerObjectType`
  - `IoDeviceHandlerObjectSize`
- `IoAllocateAdapterChannel()`:
  - Uses the device object's embedded wait context block.
  - Fills `DeviceObject`, caller context, and current IRP into the WCB.
  - Calls `HalAllocateAdapterChannel()` with the adapter object, WCB, requested map-register count, and execution routine.

## Research Notes

This is a thin compatibility wrapper around HAL DMA adapter channel allocation. The important state transfer is from `DeviceObject->CurrentIrp` and caller context into `DeviceObject->Queue.Wcb` before delegating to HAL.
