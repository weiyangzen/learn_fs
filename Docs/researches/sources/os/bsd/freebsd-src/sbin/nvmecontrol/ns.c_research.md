# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/ns.c

Purpose: Implements `nvmecontrol ns` namespace-management subcommands.

Key behavior:
- Registers `ns` with subcommands: `active`, `allocated`, `controllers`, `create`, `delete`, `attach`, `detach`, `attached`, and `identify`.
- Normalizes namespace device paths to controller paths when needed using `get_nsid()`.
- Checks controller support for namespace management via `NVME_CTRLR_DATA_OACS_NSMGMT`.
- Uses `NVME_OPC_IDENTIFY` CNS values to list active namespaces, allocated namespaces, subsystem controllers, attached controllers, and allocated namespace identify data.
- Uses `NVME_OPC_NAMESPACE_MANAGEMENT` for create/delete.
- Uses `NVME_OPC_NAMESPACE_ATTACHMENT` for attach/detach.
- Provides human-readable command-specific status strings for namespace-management failures.

Important internals:
- `nscreate()` builds a `struct nvme_namespace_data`, defaults capacity to namespace size, defaults LBA format/protection settings when absent, and swaps namespace data to little endian before submission.
- `nsdelete()` accepts either namespace device context or explicit `--namespace-id`.
- `nsattach()` can attach to all subsystem controllers or a specific/default controller.
- `nsdetach()` can detach from all currently attached controllers or a specific/default controller.
- `nsidentify()` can print parsed namespace data or hex, trimming trailing zeroes unless verbose.

Dependencies:
- `nvmecontrol.h` for command registration and helper routines.
- FreeBSD NVMe passthrough ioctls and NVMe identify/namespace structures.

Research notes:
- All mutating operations open the controller for write.
- Several commands intentionally require explicit namespace IDs when invoked on a controller device.
