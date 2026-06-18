# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_subr.c

Read completely: 755 lines.

Implements root-device and dump-device selection during boot, including interactive root selection, NFS-root heuristics, memory-disk root handling, boot spec parsing, root hooks, wedge swap detection, and root/dump announcement.

Boot/root state:
- Defines `booted_device`, `booted_method`, `booted_partition`, `booted_startblk`, `booted_nblks`, and `bootspec`.
- Defines `dumpcdev` for savecore.
- `md_is_root` is initialized from `MEMORY_DISK_IS_ROOT`.
- `ROOT_WAITTIME` controls how long `setroot()` waits for a specified root device to appear before asking.

Root selection:
- `setroot()` normalizes `rootspec`, forces memory-disk root when requested, optionally handles TFTPROOT, applies NFS-root heuristics, enters ask mode when needed, and loops until `root_device` is set.
- `setroot_nfs()` chooses a non-loopback, non-point-to-point network interface as `rootspec` when the root filesystem is NFS and the boot device is missing or not a network interface.
- `setroot_md()` opens `md0` and rewrites the boot device to the memory disk if available.
- `setroot_root()` resolves non-interactive root selection from wildcard boot device, explicit `rootspec`, or existing `rootdev`.

Interactive selection:
- `setroot_ask()` prompts for root device, dump device, and filesystem type.
- It accepts defaults, wildcard `*`, `none` for dumps, `halt`, `reboot`, and optionally `ddb`.
- It updates `rootdev`, `dumpdev`, `rootfstype`, prints the chosen root, and calls `setroot_dump()`.

Dump device:
- `setroot_dump()` applies three rules: use the already selected interactive dump device, honor `dumpspec`, or default to root partition `b` for partitioned disks.
- For root devices without partitions, it searches configured devices for a `dk` wedge whose partition type is swap.
- It sets `dumpdev` and `dumpcdev`, or clears both to `NODEV`.

Parsing and device lookup:
- `finddevice()` first consults root-spec hooks, then falls back to `device_find_by_xname()`.
- `getdisk()` wraps `parsedisk()` and prints valid device alternatives on failure.
- `parsedisk()` parses optional partition suffixes, root-spec hooks, disk devices, network interfaces, and constructs `dev_t` values with or without partitions.
- `isswap()` opens a `dk` wedge, queries `DIOCGWEDGEINFO`, and checks for `DKW_PTYPE_SWAP`.

Notes:
- Despite living in `sys/kern`, this file is directly relevant to filesystem startup because it chooses the root filesystem device and dump device.
- The code supports network roots and disk roots uniformly through `device_class()` and `device_has_partitions()`.
