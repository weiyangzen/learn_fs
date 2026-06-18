# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fssnap_if.h

## Role

`fssnap_if.h` defines the public control ABI and kernel dispatch interface for filesystem snapshots. It covers ioctls used by `fssnapctl`, filesystem-to-snapshot communication, snapshot device naming, error codes, kstat names, and kernel operation vectors.

## Key Interfaces and Data

- `struct fiosnapcreate` describes single-backing-file snapshot creation inputs and outputs.
- `struct fiosnapcreate_multi` extends creation to multiple backing files with a flexible one-element descriptor array.
- `struct fiosnapdelete` carries root filesystem descriptor, snapshot number, and result error.
- Packing is adjusted on LP64 systems where 64-bit and 32-bit long-long alignment differ, preserving x86/amd64 structure compatibility.
- Defines `FIOCOW_*` snapshot creation/delete error codes for readonly filesystems, busy snapshots, lock/flush/clean failures, bad chunk size, create failure, bitmap failure, and bad backing files.
- Defines snapshot device constants: `SNAP_CTL_MINOR`, `SNAP_NAME`, `SNAP_CTL_NODE`, block and raw character names.
- Defines kstat names for high-water mark, mount point, backing filename, and numeric stats.
- Kernel-only `struct fssnap_operations` is the loadable snapshot subsystem operation table: create, set/is candidate, create_done, delete, and strategy.
- Declares `snapops` and wrapper functions `fssnap_init()`, `fssnap_fini()`, `fssnap_create()`, `fssnap_delete()`, and related helpers.

## Dependencies and Use

The file includes `sys/types.h` and `sys/fssnap.h`, so kernel consumers inherit `chunknumber_t` and snapshot COW structures. Filesystems use this as the indirection boundary to the snapshot subsystem.

## Research Notes

This is both an ioctl ABI and an in-kernel plugin ABI. The comments explicitly call out cross-architecture packing, making structure layout part of the compatibility surface.
