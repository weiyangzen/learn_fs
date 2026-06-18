<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/device-discovery.c -->
# sources/user-network-fs/nfs-utils/utils/blkmapd/device-discovery.c

## Purpose
This is the `blkmapd` daemon entry point. It discovers local block devices for pNFS block layout use, watches `rpc_pipefs` for the kernel's `nfs/blocklayout` pipe, receives mount/unmount device requests, and replies with either created device-mapper major/minor numbers or an error status.

## APIs And Control Flow
Key routines are `bl_discover_devices`, `bl_disk_inquiry_process`, `bl_event_helper`, and `main`. Discovery clears `visible_disk_list`, reads `/proc/partitions`, keeps only whole block devices present under `/sys/block`, and calls `bl_add_disk` for `/dev/<name>`. `bl_add_disk` opens the device, determines size, reads SCSI serial/path state through `device-inq.c`, groups paths by serial, and chooses the highest priority path: pseudo, active, then passive. The event loop uses `inotify` for pipefs topology changes and `select` for the pipe itself. Mount requests call `process_deviceinfo`; unmount requests call `dm_device_remove_all`.

## State, Dependencies, And Integration
Persistent process state includes pipe paths, watch descriptors, pipe fd, pidfile fd, and the global `visible_disk_list`. It depends on Linux block ioctls, inotify, syslog, `/proc/partitions`, `/sys/block`, `/dev`, rpc_pipefs, libdevmapper helpers, and nfs-utils config parsing for `pipefs-directory`.

## Risks And Test Signals
Risks include fallback serials based on filenames causing unstable identity, a possible null dereference when serial reading fails but later serial comparison assumes `serial`, pidfile locking in the parent rather than daemon child, fixed pipe message framing with poor resynchronization after short reads, and path priority depending on full rediscovery timing. Test with fake pipefs create/delete events, mount/unmount pipe messages, missing pipe directories, multipath devices, SCSI inquiry failures, and daemon/foreground/pidfile modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/device-discovery.c -->
