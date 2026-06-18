# sources/user-network-fs/libfuse/util/init_script

## Purpose
Legacy SysV init script for loading the FUSE kernel module and mounting/unmounting the `fusectl` control filesystem.

## Important APIs, Types, And Functions
- LSB init actions: `start`, `restart`, `force-reload`, `stop`, and `status`.
- Uses `modprobe fuse`, `mount -t fusectl fusectl /sys/fs/fuse/connections`, `umount`, and `rmmod fuse`.

## Control Flow
Startup exits if `fusermount3` is missing, loads the module if `/proc/filesystems` lacks `fuse`, and mounts fusectl if supported and not already mounted. Stop unmounts fusectl and attempts to unload the module. Status reports whether FUSE appears in `/proc/filesystems`.

## State And Persistence
Persistent system state is kernel module load state and the fusectl mount. The script itself stores no state.

## Dependencies And Integration Points
Installed optionally by `install_helper.sh`; uses `/lib/lsb/init-functions`, `/proc/filesystems`, `/proc/mounts`, `/proc/modules`, and standard system utilities.

## Risks
Designed for older init systems; systemd/udev environments may not need it. It uses unquoted `$MOUNTPOINT` in grep/mount commands, though the constant path is safe. `stop` may fail to unload the module if connections are active.

## Test Signals
Test start/stop/status on systems with/without loaded module, with fusectl already mounted, missing `fusermount3`, failed `modprobe`, and active FUSE connections preventing `rmmod`.
