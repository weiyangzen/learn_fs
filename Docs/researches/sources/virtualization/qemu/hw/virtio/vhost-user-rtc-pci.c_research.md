# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-rtc-pci.c

## Purpose
Provides PCI transport glue for vhost-user RTC/clock.

## Key Behavior
- Embeds `VHostUserRTC`.
- Forces one MSI-X vector.
- Registers misc category and `PCI_CLASS_SYSTEM_RTC`.
- Uses non-transitional PCI type `vhost-user-rtc-pci`.

## Filesystem/Storage Relevance
No direct filesystem role; this is a small vhost-user transport wrapper.
