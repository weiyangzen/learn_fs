# File Research: sources/virtualization/guestfs-tools/ls/ls.c

## Role

C implementation of `virt-ls`, a read-only guest filesystem listing tool.

## Major Responsibilities

The program parses drive/domain/mount options and listing flags, launches libguestfs, mounts either explicit mountpoints or the inspected root, and lists one or more guest directories.

It supports four listing modes: plain `ls`, long `-l`, recursive `-R`, and long-recursive `-lR`. Many advanced flags are restricted to `-lR`: CSV output, human-readable sizes, UID/GID output, times, relative/day/time_t time formats, extra stat fields, and checksums.

## Listing Behavior

Plain mode calls `guestfs_ls`. Long mode calls `guestfs_ll`. Recursive mode calls `guestfs_find`. Long-recursive mode uses the shared `visit` helper and `show_file`, which receives statns and xattrs for each entry.

`show_file` emits file type, permissions, size, optional UID/GID, optional atime/mtime/ctime, optional device/inode/link/rdev/block fields, optional checksum for regular files, full path, and symlink target.

## Output Formatting

Output supports space-separated and CSV formats. CSV quoting is implemented locally for spaces, quotes, newlines, and commas. Size output can use gnulib `human_readable`. Device numbers are printed as major:minor. Time output can be formatted wall-clock, raw seconds, seconds before now, or days before now.

## Research Notes

This file is the core formatting implementation for `virt-ls`; tests cover both plain `/bin` output and selected `-lR` fields.
