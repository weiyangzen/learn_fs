<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/dm-device.c -->
# sources/user-network-fs/nfs-utils/utils/blkmapd/dm-device.c

## Purpose
This file translates decoded pNFS block volume graphs into Linux device-mapper devices and removes them later. It is the backend that turns simple, slice, concat, and stripe layout descriptions into `/dev/mapper/pnfs_vol_N` devices.

## APIs And Control Flow
Internal helpers maintain linked lists of DM target table rows and tracked `dm_tree` objects. `dm_device_create_mapped` creates a DM device, sets its generated name, adds all targets, runs the task, updates nodes, and returns `MKDEV(major, minor)`. `dm_device_remove` finds a mapper device name by dev number before removing it. `dm_device_remove_all` maps a kernel-provided major/minor pair to a tracked DM tree, removes the root, deactivates children, updates nodes, and drops the cached tree. `dm_device_create` walks decoded volumes in order, passing through simple devices and creating linear or striped targets for slices, concats, and stripes. Each created pseudo volume rewrites the current volume to `BLOCK_VOLUME_PSEUDO`.

## State, Dependencies, And Integration
Global state includes `dev_count` for generated names and `bl_tree_head` for removal tracking. It depends on libdevmapper, `/dev/mapper`, Linux device number macros, and the decoded `bl_volume` graph from `device-process.c`.

## Risks And Test Signals
Risks include fixed target parameter buffers, generated-name races with other processes, removal limited to devices tracked in this process, sparse error cleanup, `del_from_bl_dm_tree` predecessor handling, and assumptions that subvolumes are already simple/pseudo. Test with mocked libdevmapper for creation failure, name collision, concat table offsets, stripe parameter formatting, child cleanup, and process restart before unmount.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/dm-device.c -->
