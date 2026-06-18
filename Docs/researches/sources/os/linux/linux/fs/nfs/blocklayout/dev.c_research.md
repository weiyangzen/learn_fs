# File Research: sources/os/linux/linux/fs/nfs/blocklayout/dev.c

## Purpose
Implements pNFS block layout device-id decoding and device mapping. It turns XDR-encoded pNFS block volume descriptions into `pnfs_block_dev` trees backed by local block devices, including simple, sliced, concatenated, striped, and SCSI persistent-reservation-capable volumes.

## Main Responsibilities
- Decode pNFS block volume records from `GETDEVICEINFO` XDR payloads.
- Resolve simple volumes through the blocklayout userspace pipefs helper.
- Resolve SCSI volumes through stable `/dev/disk/by-id/` names.
- Open block devices for read/write access and attach them to device-id nodes.
- Build recursive device trees for slices, concatenations, and stripes.
- Register/unregister SCSI persistent reservation keys where required.
- Map logical block-layout offsets to underlying block devices and disk offsets.

## Key Functions
- `bl_register_dev()` recursively registers leaf SCSI devices with persistent reservations and unwinds partial success on failure.
- `bl_free_deviceid_node()` frees an NFS device-id node, recursively unregistering reservations, releasing child arrays, and `fput()`ing block-device files.
- `nfs4_block_decode_volume()` decodes one volume descriptor and validates counts, signature lengths, designator lengths, and volume type.
- `bl_map_simple()`, `bl_map_concat()`, and `bl_map_stripe()` implement the logical-to-physical mapping callbacks stored in each parsed device.
- `bl_parse_simple()` asks userspace to resolve a simple signature volume to `dev_t`, then opens the block device by device number.
- `bl_parse_scsi()` validates SCSI designators, opens by-id paths, stores the PR key, and verifies the device supports reservation operations.
- `bl_parse_slice()`, `bl_parse_concat()`, and `bl_parse_stripe()` recursively assemble derived devices from earlier decoded volume indices.
- `bl_alloc_deviceid_node()` is the top-level allocator/parser used by pNFS device-id cache code.

## Control Flow
`bl_alloc_deviceid_node()` allocates an XDR scratch folio, decodes the volume count, allocates an array of `pnfs_block_volume`, decodes each volume, allocates the top `pnfs_block_dev`, and parses the last volume as the root device. The resulting `nfs4_deviceid_node` is initialized even if parsing fails; on failure it is marked unavailable.

## Data and Ownership
- `pnfs_block_dev` owns child arrays for compound devices and a `struct file *bdev_file` for leaf devices.
- Device-id nodes are freed via RCU with `kfree_rcu()`.
- Leaf block devices are released with `fput()`.
- SCSI PR registration state is tracked with `PNFS_BDEV_REGISTERED`.

## Dependencies
Uses Linux block layer APIs (`bdev_file_open_by_dev`, `bdev_file_open_by_path`, `file_bdev`, `bdev_nr_bytes`), SUNRPC XDR helpers, pNFS device-id infrastructure, and tracepoints from `nfs4trace.h`.

## Notable Details
- Simple volume decoding preserves a byte length used later by `rpc_pipefs.c` to re-encode the volume for userspace.
- SCSI resolution tries `dm-uuid-mpath-0x`, then `wwn-0x`, then `nvme-eui.` path prefixes.
- SCSI designator support is deliberately narrow: EUI64 and NAA binary designators are accepted; T10 and NAME are rejected.
- Stripe mapping computes the child index from logical chunk number and child count, then maps through the child.

## Risks and Edge Cases
- Recursive parse failures in concat/stripe can leave partially initialized children, but final device free paths can clean recursively once attached.
- Stripe parsing does not validate `chunk_size` for zero before use; correctness depends on server-provided layout validity.
- `nr_volumes` is used for allocation and indexing without an explicit upper bound at the top level; individual child lists are bounded by `PNFS_BLOCK_MAX_DEVICES`.
- SCSI PR support is mandatory for SCSI layouts; devices without `pr_ops` fail parsing.

## Integration Points
This file is used by the pNFS block layout driver’s device-id cache and layout I/O path. `bl_resolve_deviceid()` is implemented in `rpc_pipefs.c`, while extent-to-device mapping is consumed by the block layout read/write path outside this file.
