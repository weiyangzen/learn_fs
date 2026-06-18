# File Research: sources/virtualization/libblockdev/src/plugins/fs/Makefile.am

## Role

`fs/Makefile.am` defines the Automake build for the libblockdev filesystem plugin library `libbd_fs.la`.

## Build Configuration

It sets:

- `AUTOMAKE_OPTIONS = subdir-objects`
- compiler flags from GLib, GIO, blkid, libmount, UUID, and ext2fs
- strict warnings with `-Wall -Wextra -Werror`, while allowing selected warning classes
- linkage against libblockdev utils and required external libraries
- version info `3:0:0`
- no undefined symbols
- exported symbols matching `^bd_.*`

## Source List

The library includes the top-level fs dispatcher and all filesystem modules:

- common helpers
- ext
- generic
- mount
- ntfs
- vfat
- xfs
- f2fs
- nilfs
- exfat
- btrfs
- udf
- shared `check_deps`

## Installed Headers

It installs per-filesystem headers under `$(includedir)/blockdev/fs/`.

## Notable Risks

- New filesystem modules must be added to both `libbd_fs_la_SOURCES` and `libincludefs_HEADERS`.
- Export policy is broad for `bd_.*`; internal functions avoid that prefix or use `G_GNUC_INTERNAL`.
