# File Research: sources/virtualization/libguestfs/lib/create.c

## Role
Implements host-side APIs for creating empty raw and qcow2 disk images.

## Public Entry
`guestfs_impl_disk_create()` validates size/backing-file semantics, dispatches to raw or qcow2 creation, and rejects unsupported formats.

## Raw Creation
- Rejects backing files and raw-incompatible options.
- Supports sparse/off or full preallocation.
- Refuses to overwrite character devices.
- For block devices, attempts `BLKDISCARD` instead of recreating the target.
- For files, creates/truncates the file and uses `ftruncate()` for sparse or `posix_fallocate()`/zero-write emulation for full allocation.

## Qcow2 Creation
- Validates backing format, preallocation, compat (`0.10` or `1.1`), and power-of-two cluster size between 512 and 2 MiB.
- Infers backing format with `guestfs_disk_format()` when a backing file is used and no format is supplied.
- Builds `qemu-img create -f qcow2` with escaped `-o` options.
- Prefixes relative filenames with `./` to avoid qemu protocol interpretation.
- Captures qemu output for error reporting/debug logging.

## Filesystem/Storage Relevance
This file creates virtual disks that are later partitioned, formatted, mounted, or used as backing images.
