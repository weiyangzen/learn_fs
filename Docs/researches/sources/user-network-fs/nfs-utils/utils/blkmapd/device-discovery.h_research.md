<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/device-discovery.h -->
# sources/user-network-fs/nfs-utils/utils/blkmapd/device-discovery.h

## Purpose
This header defines the shared block-layout discovery contract used by `blkmapd` source files: decoded block volume structures, disk identity structures, pipe message formats, XDR-style decode helpers, public daemon functions, and logging macros.

## APIs And Types
Important types are `enum blk_vol_type`, `struct bl_volume`, `struct bl_sig`, `struct bl_disk`, `struct bl_disk_path`, `struct bl_serial`, `struct bl_dev_msg`, and `struct bl_pipemsg_hdr`. Volume types model simple devices, slices, concats, stripes, and pseudo devices. Disk offsets and lengths are stored in 512-byte sectors. `BLK_READBUF`, `READ32`, `READ64`, and `READ_SECTOR` are decode macros layered on `blk_overflow`. Public functions connect the modules: `bl_discover_devices`, `process_deviceinfo`, `dm_device_create`, `dm_device_remove_all`, SCSI serial helpers, and `atomicio`.

## State, Dependencies, And Integration
The header exposes `visible_disk_list` as global shared daemon state and assumes networking byte-order helpers, syslog, device major/minor types, and block-device semantics. It is the integration point between discovery, SCSI inquiry, pNFS deviceinfo decoding, and device-mapper creation.

## Risks And Test Signals
Risks include macro-based decode control flow that jumps to `out_err`, flexible-array `struct bl_dev_id` layout assumptions over raw SCSI buffers, sector-alignment rejection in `READ_SECTOR`, and exposing mutable global disk state. Tests should cover malformed short buffers, unaligned 64-bit sector fields, maximum signature component counts, and compile coverage for all modules including this header.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/device-discovery.h -->
