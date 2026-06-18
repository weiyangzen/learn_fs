# File Research: sources/virtualization/guestfs-tools/make-fs/make-fs.c

## Role

C implementation of `virt-make-fs`, which creates a disk image containing a filesystem populated from a directory, tar archive, or compressed tar archive.

## Major Responsibilities

The tool parses output format, filesystem type, partitioning, label, size, floppy shortcut, block size, verbose/debug, version, and tracing options. It expects exactly `input output.img`.

It estimates input size, adds overhead for partition alignment, filesystem metadata, journals, btrfs metadata, xfs minimum size, and a 10% margin, then creates the output disk with `guestfs_disk_create_argv`. For qcow2 it requests metadata preallocation.

## Input Handling

Directories are measured with `du --apparent-size -b -s` and later converted to tar through a background `tar -C input -cf - .`. Non-directories are classified with `file -bsSLz`; plain tar files use file size, while compressed tar archives are decompressed through `uncompress`, `gzip`, `bzip2`, or `xz` to count bytes and later feed `guestfs_tar_in` through `/dev/fd`.

## Filesystem Creation

The tool can create raw or partitioned images. Partitioned images call `guestfs_part_disk` and set known MBR type IDs for FAT, NTFS, ext, and minix. Non-btrfs filesystems use `guestfs_mkfs_opts_argv`; btrfs uses `guestfs_mkfs_btrfs_argv` with single data/metadata profiles. VFAT mounts with `utf8`.

## Research Notes

The implementation coordinates host subprocesses and libguestfs operations. Failure paths keep the output image under cleanup control until the function completes successfully.
