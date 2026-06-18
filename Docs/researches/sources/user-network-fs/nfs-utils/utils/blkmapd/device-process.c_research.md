<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/device-process.c -->
# sources/user-network-fs/nfs-utils/utils/blkmapd/device-process.c

## Purpose
This file decodes XDR-like pNFS block layout deviceinfo sent by the kernel, maps server-provided signatures to discovered local disks, builds an internal `bl_volume` graph, and asks `dm-device.c` to materialize the final block device.

## APIs And Control Flow
`blk_overflow` bounds-checks decode cursor movement. `decode_blk_signature` reads signature components and points them directly into the input buffer. `verify_sig` opens a candidate disk and requires every component to match at absolute or end-relative offsets. `map_sig_to_device` scans `visible_disk_list` and fills simple volume device and size fields. `decode_blk_volume` handles simple, slice, stripe, and concat volumes; slices read offset/size and one prior volume; stripes validate power-of-two stripe units and equal subvolume sizes; concats sum subvolume sizes. `process_deviceinfo` reads the volume count, allocates the volume array and pointer arena, decodes all volumes in order, verifies complete consumption, calls `dm_device_create`, and returns major/minor.

## State, Dependencies, And Integration
The module depends on `visible_disk_list`, device paths chosen by discovery, network-byte-order fields, Linux major/minor macros, and device-mapper creation. It does not persist state itself; created DM devices are tracked by `dm-device.c`.

## Risks And Test Signals
Risks include raw input pointer aliasing, potentially insufficient pointer-arena sizing if future volume rules change, O(n disks * signatures) scanning, read/lseek assumptions on block devices, and rejecting valid but non page-size stripe units per DM constraints. Tests should fuzz short buffers, invalid indices, negative offsets, unmatched signatures, mixed stripe sizes, and successful simple/slice/concat/stripe mappings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/device-process.c -->
