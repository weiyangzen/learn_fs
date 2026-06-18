# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sbp2/bus.h

## Role

SBP-2 bus-provider interface header. It defines the callback contract between the SBP-2 layer and an underlying serial bus implementation.

## Key Elements

- Defines SBP-2 bus interface revision.
- `sbp2_bus_buf_t` describes a bus/DMA buffer, including free-list link, bus handle, SBP-2 private data, length, flags, DMA flags, kernel address, physical/bus address, and quadlet/block read/write callbacks.
- Buffer flags distinguish DMA, read, write, posted, read/write, and write-posted buffers.
- Buffer request return codes distinguish success, generic failure, bad length, and busy device.
- `sbp2_bus_t` holds static bus parameters and function pointers for:
  interrupt-cookie lookup, node ID lookup, buffer allocation/free/sync, completion notifications, command allocation/free, and quadlet/block read/write bus transactions.

## Dependencies and Coupling

Includes `sbp2/common.h` and uses STREAMS `mblk_t`, DDI interrupt cookies, and SBP-2 buffer callbacks. The actual bus provider supplies all transport operations.

## Research Notes

This header abstracts FireWire/serial-bus operations away from SBP-2 target/session logic. Buffers can also expose remote read/write callbacks for address space exported to devices.
