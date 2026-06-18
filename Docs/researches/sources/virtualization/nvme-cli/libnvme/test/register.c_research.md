# File Research: sources/virtualization/nvme-cli/libnvme/test/register.c

## Role

`register.c` is a hardware-oriented utility that maps an NVMe controller PCI resource BAR and prints decoded NVMe controller registers.

## Behavior

`main()` expects an `nvme<X>` controller name, builds `/sys/class/nvme/<name>/device/resource0`, opens it read-only synchronous, maps one page, calls `nvme_print_registers()`, unmaps, and exits.

`nvme_print_registers()` reads 32-bit and 64-bit MMIO registers using endian-safe helpers, then prints raw register values and decoded bitfields for CAP, VS, INTMS/INTMC, CC, CSTS, NSSR, AQA, ASQ/ACQ, CMB, boot partition, PMR, and related capability/status registers.

## Dependencies

- Linux sysfs PCI resource layout.
- `mmap()`, `open()`, and page-size APIs.
- NVMe register offsets and field macros from libnvme.
- CCAN endian helpers.

## Filesystem/Storage Relevance

This is storage device introspection tooling. It interacts with sysfs and PCI MMIO rather than filesystem data structures.
