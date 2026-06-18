# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/msdos_fs.h

Defines MS-DOS/FAT directory constants and the packed on-disk directory-entry layout.

Key elements:
- Constants for sector size, directory-entry density, FAT attribute bits, deleted/free markers, and fixed 8.3 names.
- `struct msdos_dir_entry` maps the 32-byte FAT directory entry with timestamps, cluster fields, and file size.
- ReactOS packing uses `pshpack1.h`/`poppack.h`; GCC builds also use `__attribute__((packed))`.

Dependencies:
- Included by checker headers such as `file.h` and `fsck.fat.h`.

Research notes:
- `SECTOR_SIZE` is fixed at 512 here; formatter code separately uses disk geometry bytes per sector.
- `IS_FREE` treats zero name byte and deleted marker as free directory entries.
