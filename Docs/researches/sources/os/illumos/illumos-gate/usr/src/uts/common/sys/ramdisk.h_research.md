# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ramdisk.h

## Role

`ramdisk.h` defines the ramdisk driver names, admin ioctl ABI, OBP/pseudo ramdisk naming helpers, and kernel-private ramdisk device state.

## User/Admin ABI

The control device is `/dev/ramdiskctl`; block and character devices are under `/dev/ramdisk/<name>` and `/dev/rramdisk/<name>`. Minor 0 is reserved for the control node.

The private `ramdiskadm` ioctl interface uses:
- `RD_CREATE_DISK`
- `RD_DELETE_DISK`

`struct rd_ioctl` carries a fixed-size ramdisk name and 64-bit size. Only disks created through `RD_CREATE_DISK` are deletable through this interface.

## Naming and Limits

The header defines:
- `RD_MAX_DISKS` as 1024.
- `RD_NAME_LEN` as 32.
- property names `Nblocks` and `Size`.
- macros to strip OBP `ramdisk-` prefixes and pseudo-device `,raw` suffixes.

## Kernel State

`rd_devstate_t` represents one ramdisk:
- lock, name, devinfo, minor, size.
- either OBP existing physical ranges or allocated physical pages.
- virtual window mapping metadata.
- block/char/layered open counters.
- fake geometry: `dk_geom`, `vtoc`, `dk_cinfo`.
- kstat lock and kstat pointer.

Kernel defaults include 32 active disks, 25% physical memory cap, and default maxphys of 63 KiB.

## Research Notes

This header bridges admin tooling, firmware-created ramdisks, pseudo ramdisks, and disk-label emulation. The mutually exclusive OBP-range versus allocated-page representation is a key invariant.
