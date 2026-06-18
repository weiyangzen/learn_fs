# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/kioxia.h

## Purpose

`nvme/kioxia.h` is the Kioxia vendor aggregation header for uncommitted NVMe vendor-specific interfaces.

## Main Interfaces

It includes `sys/nvme/kioxia_cd8.h` and defines the Kioxia PCI vendor ID:

- `KIOXIA_PCI_VID` = `0x1e0f`

## Runtime Use

There is no runtime logic. Consumers include this header to get common Kioxia vendor IDs and the currently known Kioxia device-family definitions.

## Dependencies

Depends on `kioxia_cd8.h`.

## Risks and Invariants

The header explicitly states that the interface is not committed. Consumers should not treat these definitions as stable public ABI beyond matching the illumos/libnvme version they were built against.
