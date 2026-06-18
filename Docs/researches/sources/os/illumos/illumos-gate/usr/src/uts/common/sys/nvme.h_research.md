# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme.h

## Purpose

`nvme.h` is the central shared ABI header between `nvme(4D)` and libnvme/userland. It defines NVMe ioctl numbers, ioctl payload structures, detailed driver-specific error reporting, identify/log/feature data structures, completion status constants, namespace state reporting, and ILP32 compatibility structures.

## Main Interfaces

The ioctl namespace is rooted at `NVME_IOC` and includes controller info, identify, get log page, get feature, format, blkdev attach/detach, firmware download/commit, vendor passthrough, namespace info, locks, controller attach/detach, namespace create/delete, and helpers `IS_NVME_IOC()` and `NVME_IOC_CMD()`.

`nvme_ioctl_errno_t` is a large driver error taxonomy. It separates kernel ioctl transport errors from semantic NVMe validation errors and controller completion errors. It covers controller death/removal, namespace targeting, lock requirements, log page validation, DMA/PRP/user-buffer faults, identify validation, vendor command validation, blkdev state, format and firmware failures, feature validation, lock sequencing, namespace management, and namespace create errors.

Every ioctl payload starts with `nvme_ioctl_common_t`, which carries `nioc_nsid`, `nioc_drv_err`, and optional controller SCT/SC status. Major ioctl structures include identify, get feature, get log page, passthrough, firmware load/commit, format, lock/unlock, namespace create, controller info, and namespace info.

The header defines NVMe version helpers, namespace constants, packed 128-bit integer representation, identify controller and namespace structures, identify lists/descriptors, primary-controller capabilities, completion status fields, log page IDs, log page structures, feature IDs and feature payload encodings, firmware constants, completion status codes, namespace state enum, and command set identifiers.

The identify controller and namespace structures are full packed mirrors of NVMe specification data, including fields through recent NVMe 2.x/2.3 additions such as FDP, device personalities, power measurement, reachability, dispersed namespaces, and power limit support.

## Runtime Use

The header itself contains no functions. Runtime behavior is defined by the ABI contracts:

1. Userland fills an ioctl structure with a common header and command-specific fields.
2. `nvme(4D)` validates namespace/minor targeting, controller capability, version support, field ranges, lock state, buffer sizes, and command support.
3. On success, data is copied to/from the supplied user pointer or returned in command result fields.
4. On failure after initial ioctl setup, `nioc_drv_err` identifies the precise semantic error, avoiding overloaded `errno` meanings.

The packed NVMe data structures are also used to interpret controller identify buffers and log-page payloads returned by hardware.

## Dependencies

Kernel builds use `sys/types32.h` for 32-bit ioctl compatibility. Userland builds use `sys/uuid.h` and `<stdint.h>`. The header also depends on `sys/types.h`, `sys/debug.h`, and `sys/stddef.h`.

Related users include the NVMe driver, libnvme discovery/control APIs, and the vendor-specific NVMe headers in `sys/nvme/`.

## Risks and Invariants

This is an ABI header. Structure layout, packing, enum values, ioctl numbers, and field sizes must remain stable or intentionally versioned.

The 32-bit ioctl structures under `_KERNEL && _SYSCALL32` must match ILP32 layout exactly; pointer-size or packing mistakes break 32-bit userland.

Packed bitfields mirror hardware/spec layout and can be sensitive to compiler, endian, and specification changes. Existing `CTASSERT()` checks protect selected structure sizes and offsets.

There is a duplicate `#define NVME_FEAT_IO_CMD_SET 0x19`; it is harmless because both definitions are identical, but it is a maintenance smell.

The file intentionally distinguishes range, unsupported, and unusable errors. New ioctl validation should preserve that taxonomy so libnvme can present precise diagnostics.
