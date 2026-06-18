# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cmlb_impl.h

`cmlb_impl.h` is the private state layout for common media labeling. It defines fdisk partition counts, system partition maps, special minor nodes (`P0_RAW_DISK`, fdisk p1-p4), log masks, label validity constants, 1TB/2TB VTOC limits, and minor decoding macros.

The core `cmlb_lun` state tracks device info, target ops/cookie, lock, current label type/state, VTOC/EFI data, maps, geometry, capacity, partition/minor-node state, removable/hotplug flags, and behavior flags. Callback macros wrap target read/write/getinfo operations.
