# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dumpadm.h

This small header defines the `/dev/dump` ioctl command namespace and dump configuration flags used by dump administration tools and kernel dump configuration code.

Key contents:
- Dump ioctl base `DDIOC`.
- `/dev/dump` ioctls:
  - `DIOCGETDUMPSIZE`
  - `DIOCGETCONF`
  - `DIOCSETCONF`
  - `DIOCGETDEV`
  - `DIOCSETDEV`
  - `DIOCTRYDEV`
  - `DIOCDUMP`
  - `DIOCSETUUID`
  - `DIOCGETUUID`
  - `DIOCRMDEV`
- Kernel-controlled dump state flags:
  - `DUMP_EXCL`
  - `DUMP_STATE`
- User-controlled mutually exclusive dump content flags:
  - `DUMP_KERNEL`
  - `DUMP_ALL`
  - `DUMP_CURPROC`
  - `DUMP_CONTENT`

Dependencies:
- No included headers.
- Uses C++ guards.

Research notes:
- This is a device-control ABI for dump configuration.
- Its content flags mirror the crash dump content flags in `dumphdr.h`.
- Filesystem/storage relevance is direct: dump configuration selects and controls the dump device, often a disk/swap-backed storage target.
