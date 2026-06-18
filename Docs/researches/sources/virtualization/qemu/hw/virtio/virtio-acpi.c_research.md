# File Research: sources/virtualization/qemu/hw/virtio/virtio-acpi.c

## Purpose
Builds ACPI DSDT entries for MMIO virtio devices.

## Key Elements
- `virtio_acpi_dsdt_add()` iterates `num` devices starting at `start_index`.
- For each device, creates `VR%02u` ACPI device with `_HID` `LNRO0005`, `_UID`, and `_CCA=1`.
- Creates `_CRS` containing a fixed 32-bit memory resource and a level, active-high, exclusive interrupt.
- Increments base address by `size` and IRQ by one per device.

## Dependencies
Uses QEMU AML builders from `hw/acpi/aml-build.h` and `virtio-acpi.h`.

## Behavior/Risks
Assumes consecutive MMIO windows and IRQ numbers. It emits cache-coherent devices through `_CCA=1`.
