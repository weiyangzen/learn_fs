# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/sysfs.c

## Role

Provides centralized sysfs path resolution for libnvme.

## Key Content

- Defines default paths:
  - `/proc/device-tree/ibm,partition-uuid`
  - `/sys/block`
  - `/sys/bus/pci/slots`
  - `/sys/class/nvme-subsystem`
  - `/sys/class/nvme`
  - `/sys/firmware/dmi/entries`
- Implements `make_sysfs_dir()`, which prepends `LIBNVME_SYSFS_PATH` when the environment variable is set.
- Exposes cached path accessors:
  - `libnvme_subsys_sysfs_dir()`
  - `libnvme_ctrl_sysfs_dir()`
  - `libnvme_ns_sysfs_dir()`
  - `libnvme_slots_sysfs_dir()`
  - `libnvme_uuid_ibm_filename()`
  - `libnvme_dmi_entries_dir()`

## Dependencies

- Includes standard I/O and allocation headers plus internal `private.h`.

## Research Notes

Each accessor stores the computed path in a function-local static pointer. If `LIBNVME_SYSFS_PATH` is set, `asprintf()` allocates the prefixed string and the static pointer retains it for process lifetime. This is useful for tests, containers, or alternate sysfs roots.

## Filesystem/Storage Relevance

This file controls where libnvme looks for kernel block and NVMe topology information. The override mechanism is important for testing sysfs-backed storage discovery without requiring real hardware.
